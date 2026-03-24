from PySide6.QtWidgets import QWidget

from ui.ui_out_widget import Ui_out_widget
from models import MidiOutConfig, KeyOutConfig

class OutWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_out_widget()
        self.ui.setupUi(self)

    def load(self, midi_out_config: MidiOutConfig, key_out_config: KeyOutConfig):
        self.ui.midi_out_group_box.load(midi_out_config)
        self.ui.key_output_group_box.load(key_out_config)