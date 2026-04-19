from PyQt6.QtWidgets import QWidget

from app.panels.generated.tools_panel_ui import Ui_ToolsPanel


class ToolsPanel(QWidget):
    """Left dock — tool-specific controls."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_ToolsPanel()
        self.ui.setupUi(self)
