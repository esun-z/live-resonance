from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Slot
from utils.ui_constants import UIConstants

class PianoKeyButton(QPushButton):
    def __init__(self, is_black: bool, parent=None) -> None:
        super().__init__(parent)
        self.is_black = is_black
        # self.setCheckable(True)
        # self.setChecked(False)

        # set size
        if is_black:
            self.setFixedSize(UIConstants.white_key_width * UIConstants.black_key_width_ratio, 
                              UIConstants.white_key_height * UIConstants.black_key_height_ratio)
            self.setStyleSheet(self._get_style(is_black, False))
        else:
            self.setFixedSize(UIConstants.white_key_width, UIConstants.white_key_height)
            self.setStyleSheet(self._get_style(is_black, False))
            
    def _get_style(self, is_black: bool, checked: bool) -> str:
        if is_black:
            bg = UIConstants.selected_key_color if checked else UIConstants.black_key_color
            color = UIConstants.white_key_color
        else:
            bg = UIConstants.selected_key_color if checked else UIConstants.white_key_color
            color = UIConstants.black_key_color
        boarder = UIConstants.key_boarder_color
        font_size = f"{UIConstants.key_font_size}pt"
        return f"""
            background-color: {bg};
            color: {color};
            border: 1px solid {boarder};
            font-size: {font_size};
        """
    
    @Slot(bool)
    def update_select_status(self, selected: bool) -> None:
        self.setStyleSheet(self._get_style(self.is_black, selected))