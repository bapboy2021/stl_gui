from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class _Panel(QWidget):
    """Base for dock panel widgets. Subclass and replace the layout contents."""
    def __init__(self, title: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        self._build(layout)

    def _build(self, layout: QVBoxLayout):
        """Override to populate the panel. Default shows a placeholder label."""
        label = QLabel("(empty)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(label)
        layout.addStretch()


class ToolsPanel(_Panel):
    """Left dock — tool-specific controls go here."""
    def __init__(self):
        super().__init__("Tools")


class ScenePanel(_Panel):
    """Right dock — loaded geometry list / outliner."""
    def __init__(self):
        super().__init__("Scene")


class PropertiesPanel(_Panel):
    """Right dock (tabbed with Scene) — transform, material, etc."""
    def __init__(self):
        super().__init__("Properties")
