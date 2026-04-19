import numpy as np
import open3d as o3d
import open3d.visualization.rendering as rendering


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
        minor_width, major_width, tex_size,
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
    minor_width, major_width, tex_size,
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
                img[:, lo:hi] = color   # vertical stripe in texture = X line in world
            else:
                img[lo:hi, :] = color   # horizontal stripe in texture = Z line in world

    # X lines: walk from x_min in x_step increments
    x_lines = []
    n = 0
    while True:
        x = x_min + n * x_step
        if x > x_max + 1e-9:
            break
        px = round((x - x_min) / x_range * (tex_size - 1))
        x_lines.append((px, n % major_every == 0))
        n += 1
    draw_lines(x_lines, "x")

    # Z lines: walk from z_min in z_step increments
    z_lines = []
    n = 0
    while True:
        z = z_min + n * z_step
        if z > z_max + 1e-9:
            break
        pz = round((z - z_min) / z_range * (tex_size - 1))
        z_lines.append((pz, n % major_every == 0))
        n += 1
    draw_lines(z_lines, "z")

    return img
