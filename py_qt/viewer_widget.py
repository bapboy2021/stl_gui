import numpy as np
import open3d.visualization.rendering as rendering
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QPixmap


class Open3DViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._geometries = {}   # name -> (geometry, material)
        self._bg_color = [0.15, 0.15, 0.15, 1.0]

        # Spherical camera state
        self._center = np.zeros(3)
        self._distance = 3.0
        self._azimuth = 45.0   # degrees, horizontal
        self._elevation = 30.0  # degrees, vertical
        self._fov = 60.0

        self._renderer = None   # created lazily on first paint (real size known)
        self._pixmap = None
        self._dirty = True
        self._last_pos = None
        self._button = None

    # ------------------------------------------------------------------ public

    def add_geometry(self, name, geometry, material=None):
        if material is None:
            material = rendering.MaterialRecord()
            material.shader = "defaultLit"
            material.base_color = [0.7, 0.7, 0.7, 1.0]
        self._geometries[name] = (geometry, material)
        if self._renderer is not None:
            self._renderer.scene.add_geometry(name, geometry, material)
        self._fit_to_scene()
        self._dirty = True
        self.update()

    def remove_geometry(self, name):
        self._geometries.pop(name, None)
        if self._renderer is not None:
            self._renderer.scene.remove_geometry(name)
        self._dirty = True
        self.update()

    # --------------------------------------------------------------- internals

    def _get_renderer(self):
        if self._renderer is None:
            w, h = max(self.width(), 1), max(self.height(), 1)
            self._renderer = self._build_renderer(w, h)
        return self._renderer

    def _build_renderer(self, w, h):
        r = rendering.OffscreenRenderer(w, h)
        r.scene.set_background(self._bg_color)
        for name, (geom, mat) in self._geometries.items():
            r.scene.add_geometry(name, geom, mat)
        self._push_camera(r)
        return r

    def _fit_to_scene(self):
        r = self._get_renderer()
        bb = r.scene.bounding_box
        extent = np.linalg.norm(bb.get_max_bound() - bb.get_min_bound())
        if extent > 0:
            self._center = bb.get_center()
            self._distance = extent * 1.5
        self._push_camera(r)

    def _eye_up(self):
        az = np.radians(self._azimuth)
        el = np.radians(self._elevation)
        eye_dir = np.array([
            np.cos(el) * np.sin(az),
            np.sin(el),
            np.cos(el) * np.cos(az),
        ])
        eye = self._center + self._distance * eye_dir
        right = np.cross(eye_dir, [0.0, 1.0, 0.0])
        n = np.linalg.norm(right)
        right = right / n if n > 1e-6 else np.array([1.0, 0.0, 0.0])
        up = np.cross(right, eye_dir)
        return eye, up / np.linalg.norm(up)

    def _push_camera(self, renderer=None):
        r = renderer or self._renderer
        if r is None:
            return
        eye, up = self._eye_up()
        r.setup_camera(self._fov, self._center, eye, up)

    # ------------------------------------------------------------ Qt overrides

    def paintEvent(self, event):
        r = self._get_renderer()
        if self._dirty:
            img = r.render_to_image()
            arr = np.asarray(img)
            h, w = arr.shape[:2]
            qimg = QImage(arr.data, w, h, w * 3, QImage.Format.Format_RGB888).copy()
            self._pixmap = QPixmap.fromImage(qimg)
            self._dirty = False
        if self._pixmap:
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self._pixmap)
            painter.end()

    def resizeEvent(self, event):
        self._renderer = None  # rebuilt with new size on next paint
        self._dirty = True

    def mousePressEvent(self, event):
        self._last_pos = event.position()
        self._button = event.button()

    def mouseReleaseEvent(self, event):
        self._last_pos = None
        self._button = None

    def mouseMoveEvent(self, event):
        if self._last_pos is None:
            return
        dx = event.position().x() - self._last_pos.x()
        dy = event.position().y() - self._last_pos.y()
        self._last_pos = event.position()

        if self._button == Qt.MouseButton.LeftButton:
            # Orbit
            self._azimuth -= dx * 0.4
            self._elevation = float(np.clip(self._elevation + dy * 0.4, -89.0, 89.0))

        elif self._button == Qt.MouseButton.MiddleButton:
            # Pan — translate center in camera's local right/up plane
            eye, up = self._eye_up()
            forward = self._center - eye
            right = np.cross(forward, up)
            rn = np.linalg.norm(right)
            if rn > 1e-6:
                right /= rn
            speed = self._distance * 0.0015
            self._center -= dx * speed * right
            self._center += dy * speed * up

        self._push_camera()
        self._dirty = True
        self.update()

    def wheelEvent(self, event):
        factor = 0.9 if event.angleDelta().y() > 0 else 1.0 / 0.9
        self._distance = max(0.001, self._distance * factor)
        self._push_camera()
        self._dirty = True
        self.update()