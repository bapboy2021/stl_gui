from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QToolBar, QWidget, QLabel,
    QVBoxLayout, QApplication, QFileDialog, QTabWidget,
)
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import QAction, QKeySequence, QActionGroup

from py_qt.viewer_widget import Open3DViewerWidget
from py_qt.panels import ToolsPanel, ScenePanel, PropertiesPanel
from custom_primitives import GridFloor, AxisLines


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication, apply_theme_fn):
        super().__init__()
        self._app = app
        self._apply_theme = apply_theme_fn

        self.setWindowTitle("STL Viewer")
        self.resize(1400, 900)
        self.setDockNestingEnabled(True)

        self._viewer = Open3DViewerWidget(self)
        self.setCentralWidget(self._viewer)

        self._setup_menus()
        self._setup_toolbar()
        self._setup_docks()
        self._restore_layout()
        self._load_scene()

    # ------------------------------------------------------------------ menus

    def _setup_menus(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("&File")

        act = QAction("&Open STL…", self)
        act.setShortcut(QKeySequence.StandardKey.Open)
        act.triggered.connect(self._open_stl)
        file_menu.addAction(act)

        file_menu.addSeparator()

        act = QAction("E&xit", self)
        act.setShortcut(QKeySequence.StandardKey.Quit)
        act.triggered.connect(QApplication.quit)
        file_menu.addAction(act)

        # View — dock/toolbar toggles are added later in _setup_docks/_setup_toolbar
        self._view_menu = mb.addMenu("&View")

        # Theme
        theme_menu = mb.addMenu("&Theme")
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        current = QSettings("STLViewer", "MainWindow").value("theme", "dark")
        for theme in ("dark", "light"):
            act = QAction(theme.capitalize(), self)
            act.setCheckable(True)
            act.setChecked(theme == current)
            act.setData(theme)
            act.triggered.connect(lambda checked, t=theme: self._set_theme(t))
            theme_group.addAction(act)
            theme_menu.addAction(act)

    # --------------------------------------------------------------- toolbar

    def _setup_toolbar(self):
        tb = QToolBar("Main Toolbar", self)
        tb.setObjectName("toolbar_main")
        tb.setMovable(True)
        tb.setIconSize(QSize(18, 18))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        act = QAction("Open", self)
        act.setShortcut(QKeySequence.StandardKey.Open)
        act.triggered.connect(self._open_stl)
        tb.addAction(act)

        tb.addSeparator()

        # Viewport interaction mode (mutually exclusive)
        mode_group = QActionGroup(self)
        for label in ("Orbit", "Pan", "Zoom"):
            a = QAction(label, self)
            a.setCheckable(True)
            mode_group.addAction(a)
            tb.addAction(a)
        mode_group.actions()[0].setChecked(True)

        tb.addSeparator()

        # Scene overlay toggles
        self._grid_action = QAction("Grid", self)
        self._grid_action.setCheckable(True)
        self._grid_action.setChecked(True)
        self._grid_action.triggered.connect(self._toggle_grid)
        tb.addAction(self._grid_action)

        self._axis_action = QAction("Axis", self)
        self._axis_action.setCheckable(True)
        self._axis_action.setChecked(True)
        self._axis_action.triggered.connect(self._toggle_axis)
        tb.addAction(self._axis_action)

        # Let View menu show/hide the toolbar itself
        self._view_menu.addAction(tb.toggleViewAction())

    # ----------------------------------------------------------------- docks

    def _setup_docks(self):
        for area in (Qt.DockWidgetArea.LeftDockWidgetArea,
                     Qt.DockWidgetArea.RightDockWidgetArea):
            self.setTabPosition(area, QTabWidget.TabPosition.North)

        self._tools_dock = self._make_dock(
            "Tools", ToolsPanel(), Qt.DockWidgetArea.LeftDockWidgetArea,
        )

        self._scene_dock = self._make_dock(
            "Scene", ScenePanel(), Qt.DockWidgetArea.RightDockWidgetArea,
        )
        self._props_dock = self._make_dock(
            "Properties", PropertiesPanel(), Qt.DockWidgetArea.RightDockWidgetArea,
        )
        self.tabifyDockWidget(self._scene_dock, self._props_dock)
        self._scene_dock.raise_()

        # Dock visibility toggles live under View
        self._view_menu.addSeparator()
        for dock in (self._tools_dock, self._scene_dock, self._props_dock):
            self._view_menu.addAction(dock.toggleViewAction())

        self._view_menu.addSeparator()
        act = QAction("Reset Layout", self)
        act.triggered.connect(self._reset_layout)
        self._view_menu.addAction(act)

    def _make_dock(self, title: str, widget: QWidget, area) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(f"dock_{title.lower().replace(' ', '_')}")
        dock.setWidget(widget)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea  |
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea
        )
        self.addDockWidget(area, dock)
        return dock

    # --------------------------------------------------------------- actions

    def _set_theme(self, theme: str):
        self._apply_theme(self._app, theme)
        QSettings("STLViewer", "MainWindow").setValue("theme", theme)

    def _open_stl(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open STL", "", "STL files (*.stl);;All files (*)"
        )
        if path:
            pass  # TODO: load into viewer

    def _toggle_grid(self, checked: bool):
        if checked:
            grid = GridFloor(x_bounds=(-10,10), z_bounds=(-10,10),
                             x_step=1.0, z_step=1.0, show_labels=False)
            self._viewer.add_geometry("grid_floor", grid.geometry, grid.material)
        else:
            self._viewer.remove_geometry("grid_floor")

    def _toggle_axis(self, checked: bool):
        if checked:
            axis = AxisLines(length=0.25)
            self._viewer.add_geometry("axis", axis.geometry, axis.material)
        else:
            self._viewer.remove_geometry("axis")

    # ------------------------------------------------------------- scene init

    def _load_scene(self):
        grid = GridFloor(x_bounds=(-10,10), z_bounds=(-10,10),
                         x_step=1.0, z_step=1.0, show_labels=False)
        self._viewer.add_geometry("grid_floor", grid.geometry, grid.material)
        axis = AxisLines(length=0.25)
        self._viewer.add_geometry("axis", axis.geometry, axis.material)

    # --------------------------------------------------------- layout persist

    def _restore_layout(self):
        s = QSettings("STLViewer", "MainWindow")
        if geom := s.value("geometry"):
            self.restoreGeometry(geom)
        if state := s.value("state"):
            self.restoreState(state)

    def _reset_layout(self):
        QSettings("STLViewer", "MainWindow").clear()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,  self._tools_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._scene_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._props_dock)
        self.tabifyDockWidget(self._scene_dock, self._props_dock)
        for dock in (self._tools_dock, self._scene_dock, self._props_dock):
            dock.show()
        self._scene_dock.raise_()

    def closeEvent(self, event):
        s = QSettings("STLViewer", "MainWindow")
        s.setValue("geometry", self.saveGeometry())
        s.setValue("state",    self.saveState())
        super().closeEvent(event)
