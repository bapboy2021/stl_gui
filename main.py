import os
os.environ.pop("WAYLAND_DISPLAY", None)  # force XWayland; native Wayland crashes Open3D's XSendEvent calls

import sys
from PyQt6.QtWidgets import QApplication
from py_qt.main_window import MainWindow


def demo_o3d():
    """Open the same scene in Open3D's own visualiser (no Qt). python main.py --o3d"""
    import open3d as o3d
    import open3d.visualization.rendering as rendering
    from custom_primitives import GridFloor, AxisLines

    grid = GridFloor(x_bounds=(-10,10), z_bounds=(-10,10), x_step=1.0, z_step=1.0, show_labels=False)
    axis = AxisLines(length=0.25)
    box  = o3d.geometry.TriangleMesh.create_box()
    box.compute_vertex_normals()
    box_mat = rendering.MaterialRecord()
    box_mat.shader = "defaultLitTransparency"
    box_mat.base_color = [0.2, 0.6, 1.0, 1.0]

    o3d.visualization.draw([
        {"name": "grid", "geometry": grid.geometry, "material": grid.material},
        {"name": "axis", "geometry": axis.geometry, "material": axis.material},
        {"name": "box",  "geometry": box,           "material": box_mat},
    ])


if __name__ == "__main__":
    if "--o3d" in sys.argv:
        demo_o3d()
    else:
        app = QApplication(sys.argv)
        win = MainWindow()
        win.show()
        sys.exit(app.exec())
