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


def make_grid_floor(
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
    """
    Flat grid plane spanning x_bounds × z_bounds with UV-mapped grid texture.
    Returns (mesh, material).

    x_step / z_step  : world-unit distance between lines on each axis
    major_every      : every Nth line (counting from bounds[0]) is a major line
    """
    x_min, x_max = x_bounds
    z_min, z_max = z_bounds

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

    tex = _grid_texture(
        x_bounds, z_bounds, x_step, z_step,
        major_every, bg_color, minor_color, major_color,
        minor_width, major_width, tex_size, show_labels,
    )

    mat = rendering.MaterialRecord()
    mat.shader = "defaultUnlit"
    mat.albedo_img = o3d.geometry.Image(tex)

    return mesh, mat


def make_axis_lines(length: float = 1.5):
    """XYZ axis lines at origin. Red=X, Green=Y, Blue=Z. Returns (lineset, material)."""
    ls = o3d.geometry.LineSet()
    ls.points = o3d.utility.Vector3dVector([
        [0, 0, 0], [length, 0, 0],
        [0, 0, 0], [0, length, 0],
        [0, 0, 0], [0, 0, length],
    ])
    ls.lines = o3d.utility.Vector2iVector([[0, 1], [2, 3], [4, 5]])
    ls.colors = o3d.utility.Vector3dVector([
        [1.0, 0.15, 0.15],
        [0.15, 1.0, 0.15],
        [0.15, 0.15, 1.0],
    ])

    mat = rendering.MaterialRecord()
    mat.shader = "unlitLine"
    mat.line_width = 2.5

    return ls, mat


def _grid_texture(
    x_bounds, z_bounds, x_step, z_step,
    major_every, bg_color, minor_color, major_color,
    minor_width, major_width, tex_size, show_labels,
) -> np.ndarray:
    img = np.full((tex_size, tex_size, 3), bg_color, dtype=np.uint8)

    x_min, x_max = x_bounds
    z_min, z_max = z_bounds
    x_range = x_max - x_min
    z_range = z_max - z_min

    def draw_lines(positions_major, axis):
        for px, is_major in positions_major:
            color = major_color if is_major else minor_color
            w = major_width if is_major else minor_width
            lo = max(0, px - w // 2)
            hi = min(tex_size, px + w // 2 + 1)
            if axis == "x":
                img[:, lo:hi] = color
            else:
                img[lo:hi, :] = color

    # X lines
    x_lines, x_major = [], []
    n = 0
    while True:
        x = x_min + n * x_step
        if x > x_max + 1e-9:
            break
        px = round((x - x_min) / x_range * (tex_size - 1))
        is_major = (n % major_every == 0)
        x_lines.append((px, is_major))
        if is_major:
            x_major.append((px, f"{x:g}"))
        n += 1
    draw_lines(x_lines, "x")

    # Z lines
    z_lines, z_major = [], []
    n = 0
    while True:
        z = z_min + n * z_step
        if z > z_max + 1e-9:
            break
        pz = round((z - z_min) / z_range * (tex_size - 1))
        is_major = (n % major_every == 0)
        z_lines.append((pz, is_major))
        if is_major:
            z_major.append((pz, f"{z:g}"))
        n += 1
    draw_lines(z_lines, "z")

    if show_labels and x_major and z_major:
        img = _bake_labels(img, x_major, z_major, tex_size, x_step, z_step,
                           x_range, z_range, major_every, bg_color)

    return img


def _bake_labels(img_np, x_major, z_major, tex_size,
                 x_step, z_step, x_range, z_range, major_every, bg_color):
    """Draw major-line labels onto the texture using PIL. Labels on all 4 edges."""
    # Font size proportional to major-line spacing, capped to stay readable
    major_px = min(
        (major_every * x_step / x_range) * tex_size,
        (major_every * z_step / z_range) * tex_size,
    )
    font_size = max(9, min(18, int(major_px / 5)))
    font = _load_font(font_size)

    img_pil = Image.fromarray(img_np)
    draw = ImageDraw.Draw(img_pil)

    bg  = tuple(int(c) for c in bg_color[:3])
    fg  = (215, 215, 215)
    pad = 2

    def put(x, y, text, anchor):
        bb = draw.textbbox((x, y), text, font=font, anchor=anchor)
        draw.rectangle([bb[0]-pad, bb[1]-pad, bb[2]+pad, bb[3]+pad], fill=bg)
        draw.text((x, y), text, font=font, fill=fg, anchor=anchor)

    # X labels — top edge (z_min world) and bottom edge (z_max world)
    for px, s in x_major:
        put(px, pad,            s, "mt")
        put(px, tex_size - pad, s, "mb")

    # Z labels — left edge (x_min world) and right edge (x_max world)
    for pz, s in z_major:
        put(pad,            pz, s, "lm")
        put(tex_size - pad, pz, s, "rm")

    return np.array(img_pil)
