import os
os.environ.pop("WAYLAND_DISPLAY", None)  # force XWayland; native Wayland crashes Open3D's XSendEvent calls


import sys
import open3d as o3d
import open3d.visualization.rendering as rendering
from PyQt6.QtWidgets import QApplication, QMainWindow
from py_qt.viewer_widget import Open3DViewerWidget
from custom_primitives import GridFloor, AxisLines


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STL Viewer")
        self.resize(1024, 768)

        self._viewer = Open3DViewerWidget(self)
        self.setCentralWidget(self._viewer)
        self._load_demo()

    def _load_demo(self):
        grid = GridFloor(
            x_bounds=(-10, 10),
            z_bounds=(-10, 10),
            x_step=1.0,
            z_step=1.0,
        )
        self._viewer.add_geometry("grid_floor", grid.geometry, grid.material)

        axis = AxisLines(length=0.25)
        self._viewer.add_geometry("axis", axis.geometry, axis.material)

        box = o3d.geometry.TriangleMesh.create_box()
        box.compute_vertex_normals()
        mat_box = rendering.MaterialRecord()
        mat_box.shader = "defaultLitTransparency"
        mat_box.base_color = [0.2, 0.6, 1.0, 0.8]
        self._viewer.add_geometry("box", box, mat_box)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
