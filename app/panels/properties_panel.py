from PyQt6.QtWidgets import QWidget

from app.panels.generated.properties_panel_ui import Ui_PropertiesPanel


class PropertiesPanel(QWidget):
    """Right dock (tabbed with Scene) — transform, material, etc."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_PropertiesPanel()
        self.ui.setupUi(self)
