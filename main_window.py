from PySide6.QtWidgets import QMainWindow
import mido
from ui.ui_main_window import Ui_main_window
from models import AppConfig
from logger import get_logger
from core import MessagePlayer

class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_main_window()
        self.ui.setupUi(self)
        self.app_config = AppConfig()
        self.logger = get_logger(__name__)
        self.message_player = MessagePlayer(self.app_config.key_map, self.app_config.player)
        self.load(self.app_config)
        self.ui.midi_in_widget.message_received.connect(self.handle_message)

    def load(self, config: AppConfig) -> None:
        self.app_config = config
        self.ui.midi_in_widget.load(config.midi_in)
        self.ui.out_widget.load(midi_out_config=config.midi_out, key_out_config=config.key_out)

    def handle_message(self, msg: mido.Message) -> None:
        # self.logger.debug(f"Received MIDI message: {msg}")
        self.message_player.play_message(msg)

