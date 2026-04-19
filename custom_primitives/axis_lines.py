import open3d as o3d
import open3d.visualization.rendering as rendering


class AxisLines:
    """
    XYZ axis lines at the world origin. Red=X, Green=Y, Blue=Z.

    Usage:
        axis = AxisLines(length=0.25)
        scene.add_geometry("axis", axis.geometry, axis.material)
    """

    def __init__(self, length: float = 1.5, line_width: float = 2.5):
        self.length = length
        self.line_width = line_width

        self._geometry: o3d.geometry.LineSet | None = None
        self._material: rendering.MaterialRecord | None = None
        self.rebuild()

    @property
    def geometry(self) -> o3d.geometry.LineSet:
        return self._geometry

    @property
    def material(self) -> rendering.MaterialRecord:
        return self._material

    def rebuild(self):
        ls = o3d.geometry.LineSet()
        ls.points = o3d.utility.Vector3dVector([
            [0, 0, 0], [self.length, 0, 0],
            [0, 0, 0], [0, self.length, 0],
            [0, 0, 0], [0, 0, self.length],
        ])
        ls.lines = o3d.utility.Vector2iVector([[0, 1], [2, 3], [4, 5]])
        ls.colors = o3d.utility.Vector3dVector([
            [1.0, 0.15, 0.15],
            [0.15, 1.0, 0.15],
            [0.15, 0.15, 1.0],
        ])

        mat = rendering.MaterialRecord()
        mat.shader = "unlitLine"
        mat.line_width = self.line_width

        self._geometry = ls
        self._material = mat
