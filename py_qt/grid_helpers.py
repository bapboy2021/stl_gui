import numpy as np
import open3d as o3d
import open3d.visualization.rendering as rendering


def make_grid_floor(size: float = 20.0, cells: int = 20):
    """Flat plane with a numpy-generated grid texture. Returns (mesh, material)."""
    h = size / 2
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector([
        [-h, 0.0, -h],
        [ h, 0.0, -h],
        [ h, 0.0,  h],
        [-h, 0.0,  h],
    ])
    mesh.triangles = o3d.utility.Vector3iVector([[0, 1, 2], [0, 2, 3]])
    mesh.triangle_uvs = o3d.utility.Vector2dVector([
        [0.0, 0.0], [1.0, 0.0], [1.0, 1.0],
        [0.0, 0.0], [1.0, 1.0], [0.0, 1.0],
    ])
    mesh.compute_vertex_normals()

    mat = rendering.MaterialRecord()
    mat.shader = "defaultUnlit"
    mat.albedo_img = o3d.geometry.Image(_grid_texture(cells=cells))

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


def _grid_texture(cells: int = 20, tex_size: int = 1024) -> np.ndarray:
    img = np.full((tex_size, tex_size, 3), 30, dtype=np.uint8)
    for i in range(cells + 1):
        px = round(i * (tex_size - 1) / cells)
        is_major = (i % 5 == 0)
        color = 110 if is_major else 58
        w = 2 if is_major else 1
        lo, hi = max(0, px - w // 2), min(tex_size, px + w // 2 + 1)
        img[lo:hi, :] = color   # horizontal line
        img[:, lo:hi] = color   # vertical line
    return img
