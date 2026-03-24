from PySide6.QtWidgets import QWidget

from utils.ui_constants import UIConstants

class PianoWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.selected_note = None
        self.key_buttons = []
        