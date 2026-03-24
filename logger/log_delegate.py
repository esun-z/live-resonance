from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QColor, QPalette
import logging
from logger.log_model import LogModel

class LogDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.level_colors: dict[int, QColor] = {
            logging.DEBUG: QColor("gray"),
            logging.INFO: QColor("black"), # INFO will be chosen dynamically in paint() based on dark mode
            logging.WARNING: QColor("orange"),
            logging.ERROR: QColor("red"),
        }

    def paint(self, painter, option, index):
        log_level = index.data(LogModel.LevelRole)

        if log_level == logging.INFO:
            # determine whether the UI is in dark mode by checking window background lightness
            bg_color = option.palette.color(QPalette.Window)
            is_dark = bg_color.lightness() < 128
            text_color = QColor("white") if is_dark else self.level_colors[logging.INFO]
            option.palette.setColor(QPalette.Text, text_color)
        elif log_level in self.level_colors:
            option.palette.setColor(QPalette.Text, self.level_colors[log_level])

        super().paint(painter, option, index)