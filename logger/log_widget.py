import logging
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from ui.ui_log_widget import Ui_log_widget
from .log_model import LogModel
from .log_delegate import LogDelegate
from .qt_signal_handler import QtSignalHandler

class LogWidget(QWidget):
    DEBUGGING = True
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_log_widget()
        self.ui.setupUi(self)

        # init combo box
        self.ui.level_combo_box.clear()
        log_names = logging.getLevelNamesMapping()
        # sort by level value asc
        log_names = sorted(log_names.items(), key=lambda x: x[1])
        for name, level in log_names:
            self.ui.level_combo_box.addItem(name, level)

        self.ui.level_combo_box.setCurrentIndex(2 if not self.DEBUGGING else 1)  # Default to INFO

        # set model and delegate
        self.model = LogModel(self)
        self.model.set_min_visible_level(logging.INFO if not self.DEBUGGING else logging.DEBUG)
        self.ui.log_list_view.setModel(self.model)
        self.ui.log_list_view.setItemDelegate(LogDelegate(self.ui.log_list_view))

        # connections
        self.ui.clear_button.clicked.connect(self.clear_logs)
        self.ui.level_combo_box.currentIndexChanged.connect(self._on_filter_changed)

        # setup logging
        self._setup_logging()

    @Slot()
    def _on_filter_changed(self):
        level = self.ui.level_combo_box.currentData()
        self.model.set_min_visible_level(level)

    @Slot(int, str)
    def log_message(self, level: int, message: str):
        self.model.add_log(level, message)
        self._scroll_to_bottom()

    @Slot()
    def clear_logs(self):
        self.model.clear()

    @Slot()
    def _scroll_to_bottom(self):
        self.ui.log_list_view.scrollToBottom()

    def _setup_logging(self):

        # get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO if not self.DEBUGGING else logging.DEBUG)

        # create qt handler
        qt_handler = QtSignalHandler()
        qt_handler.setLevel(logging.INFO if not self.DEBUGGING else logging.DEBUG)

        # format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)-8s - %(message)s',
            datefmt='%H:%M:%S'
        )
        qt_handler.setFormatter(formatter)

        # connection
        qt_handler.log_signal.connect(self.log_message)

        # add handler
        root_logger.addHandler(qt_handler)
        
        # set font
        original_font = self.ui.log_list_view.font()
        font = QFont("Consolas", original_font.pointSize())
        self.ui.log_list_view.setFont(font)
