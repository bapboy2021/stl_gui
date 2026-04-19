from PyQt6.QtWidgets import QWidget

from app.panels.generated.scene_panel_ui import Ui_ScenePanel


class ScenePanel(QWidget):
    """Right dock — loaded geometry list / outliner."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_ScenePanel()
        self.ui.setupUi(self)
