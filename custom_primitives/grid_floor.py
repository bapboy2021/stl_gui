import os
import numpy as np
import open3d as o3d
import open3d.visualization.rendering as rendering
from PIL import Image, ImageDraw, ImageFont

_FONT_PATHS = [
    "/usr/share/fonts/TTF/Hack-Regular.ttf",
    "/usr/share/fonts/gnu-free/FreeMonoBold.otf",
    "/usr/share/fonts/Adwaita/AdwaitaMono-Regular.ttf",
    os.path.expanduser("~/.local/share/fonts/ComicShannsMonoNerdFontMono-Regular.otf"),
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


class GridFloor:
    """
    Open3D floor grid on the XZ plane with UV-mapped texture and baked labels.

    All settings are stored as plain attributes. Call rebuild() after changing
    any of them to regenerate the mesh and texture.

    Usage:
        grid = GridFloor(x_bounds=(-10, 10), z_bounds=(-10, 10), x_step=1.0, z_step=1.0)
        scene.add_geometry("grid", grid.geometry, grid.material)
    """

    def __init__(
        self,
        x_bounds: tuple = (-10.0, 10.0),
        z_bounds: tuple = (-10.0, 10.0),
        x_step: float = 1.0,
        z_step: float = 1.0,
        major_every: int = 5,
        bg_color: tuple = (30, 30, 30),
        minor_color: tuple = (90, 90, 90),
        major_color: tuple = (145, 145, 145),
        minor_width: int = 2,
        major_width: int = 3,
        tex_size: int = 1024,
        show_labels: bool = True,
    ):
        self.x_bounds = x_bounds
        self.z_bounds = z_bounds
        self.x_step = x_step
        self.z_step = z_step
        self.major_every = major_every
        self.bg_color = bg_color
        self.minor_color = minor_color
        self.major_color = major_color
        self.minor_width = minor_width
        self.major_width = major_width
        self.tex_size = tex_size
        self.show_labels = show_labels

        self._geometry: o3d.geometry.TriangleMesh | None = None
        self._material: rendering.MaterialRecord | None = None
        self.rebuild()

    # ------------------------------------------------------------------ public

    @property
    def geometry(self) -> o3d.geometry.TriangleMesh:
        return self._geometry

    @property
    def material(self) -> rendering.MaterialRecord:
        return self._material

    def rebuild(self):
        """Regenerate geometry and texture from current settings."""
        self._geometry = self._build_mesh()
        tex = self._build_texture()
        self._material = rendering.MaterialRecord()
        self._material.shader = "defaultUnlit"
        self._material.albedo_img = o3d.geometry.Image(tex)

    # --------------------------------------------------------------- internals

    def _build_mesh(self) -> o3d.geometry.TriangleMesh:
        x_min, x_max = self.x_bounds
        z_min, z_max = self.z_bounds

        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector([
            [x_min, 0.0, z_min],
            [x_max, 0.0, z_min],
            [x_max, 0.0, z_max],
            [x_min, 0.0, z_max],
        ])
        mesh.triangles = o3d.utility.Vector3iVector([[0, 1, 2], [0, 2, 3]])
        mesh.triangle_uvs = o3d.utility.Vector2dVector([
            [0.0, 0.0], [1.0, 0.0], [1.0, 1.0],
            [0.0, 0.0], [1.0, 1.0], [0.0, 1.0],
        ])
        mesh.compute_vertex_normals()
        return mesh

    def _build_texture(self) -> np.ndarray:
        ts = self.tex_size
        x_min, x_max = self.x_bounds
        z_min, z_max = self.z_bounds
        x_range = x_max - x_min
        z_range = z_max - z_min

        img = np.full((ts, ts, 3), self.bg_color, dtype=np.uint8)

        def draw_stripe(px, is_major, axis):
            color = self.major_color if is_major else self.minor_color
            w = self.major_width if is_major else self.minor_width
            lo = max(0, px - w // 2)
            hi = min(ts, px + w // 2 + 1)
            if axis == "x":
                img[:, lo:hi] = color
            else:
                img[lo:hi, :] = color

        # X lines — columns in the texture map to world X
        x_major = []
        n = 0
        while True:
            x = x_min + n * self.x_step
            if x > x_max + 1e-9:
                break
            px = round((x - x_min) / x_range * (ts - 1))
            is_major = (n % self.major_every == 0)
            draw_stripe(px, is_major, "x")
            if is_major:
                x_major.append((px, f"{x:g}"))
            n += 1

        # Z lines — pz is inverted so z_min lives at row ts-1 (UV v=0 in OpenGL)
        z_major = []
        n = 0
        while True:
            z = z_min + n * self.z_step
            if z > z_max + 1e-9:
                break
            pz = (ts - 1) - round((z - z_min) / z_range * (ts - 1))
            is_major = (n % self.major_every == 0)
            draw_stripe(pz, is_major, "z")
            if is_major:
                z_major.append((pz, f"{z:g}"))
            n += 1

        if self.show_labels and x_major and z_major:
            img = self._bake_labels(img, x_major, z_major)

        return img

    def _bake_labels(self, img_np, x_major, z_major) -> np.ndarray:
        """
        Bake coordinate labels onto the texture.
        X values along the bottom edge, Z values along the left edge.
        Both corner entries (x_min and z_min) are skipped so the
        bottom-left corner stays clean.
        """
        ts = self.tex_size
        x_range = self.x_bounds[1] - self.x_bounds[0]
        z_range = self.z_bounds[1] - self.z_bounds[0]

        major_px = min(
            (self.major_every * self.x_step / x_range) * ts,
            (self.major_every * self.z_step / z_range) * ts,
        )
        font_size = max(9, min(18, int(major_px / 5)))
        font = _load_font(font_size)

        img_pil = Image.fromarray(img_np)
        draw = ImageDraw.Draw(img_pil)

        bg = tuple(int(c) for c in self.bg_color[:3])
        fg = (215, 215, 215)
        pad = 2

        def put(x, y, text, anchor):
            bb = draw.textbbox((x, y), text, font=font, anchor=anchor)
            # Nudge so the padded box never bleeds outside the image
            dx = max(0, bb[2] + pad - ts) - max(0, pad - bb[0])
            dy = max(0, bb[3] + pad - ts) - max(0, pad - bb[1])
            x -= dx
            y -= dy
            bb = draw.textbbox((x, y), text, font=font, anchor=anchor)
            draw.rectangle([bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad], fill=bg)
            draw.text((x, y), text, font=font, fill=fg, anchor=anchor)

        # Bottom edge: X values. Skip x_major[0] (x_min) — bottom-left corner.
        for px, s in x_major[1:]:
            put(px, ts - pad, s, "mb")

        # Left edge: Z values. Skip z_major[0] (z_min, pz=ts-1) — bottom-left corner.
        for pz, s in z_major[1:]:
            put(pad, pz, s, "lm")

        return np.array(img_pil)
