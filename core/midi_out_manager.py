from PySide6.QtCore import QObject, Signal, Slot
import mido
from models import MidiOutConfig
from utils.midi_utils import set_message_channel
from logger import get_logger

class MidiOutManager(QObject):
    status_changed = Signal(bool, str) # status, reason

    def __init__(self, config: MidiOutConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.logger = get_logger(__name__)
        self.running = False
        self.port = None

    @Slot()
    def start(self):
        try:
            self.port = mido.open_output(self.config.device_name)
            self.running = True
            self.status_changed.emit(True, "")
        except Exception as e:
            self.logger.error(f"Error in MIDI output worker: {e}")
            self.status_changed.emit(False, str(e))

    @Slot()
    def send_message(self, message: mido.Message):
        if self.running and self.port:
            try:
                if self.config.merge_channels:
                    msg = set_message_channel(message, self.config.target_channel)
                else:
                    msg = message

                self.port.send(msg)
            except Exception as e:
                self.logger.error(f"Error sending MIDI message: {e}")
                self.running = False
                self.status_changed.emit(False, str(e))
                self.port.close()
    
    @Slot()
    def stop(self):
        if self.port:
            self.port.close()
        self.running = False
        self.status_changed.emit(False, "")