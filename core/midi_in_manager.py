from PySide6.QtCore import QObject, Signal, Slot, QThread, QCoreApplication
import mido
import time
from models import AppConfig
from logger import get_logger
from utils.midi_utils import is_message_in_channels
from .message_player import MessagePlayer

class MidiInWorker(QObject):
    # message_received = Signal(mido.Message)
    status_changed = Signal(bool, str) # status, reason

    MIDI_LISTEN_INTERVAL = 1  # ms
    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.midi_in_config = config.midi_in
        self.key_map_config = config.key_map
        self.key_out_config = config.key_out
        self.player_config = config.player
        self.logger = get_logger(__name__)
        self.running = False
        self.message_player = MessagePlayer(self.key_map_config, self.player_config, parent=self)

    @Slot()
    def start(self):
        try:
            with mido.open_input(self.midi_in_config.device_name) as port:
                self.running = True
                self.status_changed.emit(True, "")
                while self.running:
                    message = port.receive(block=False)
                    if message:
                        if not is_message_in_channels(message, self.midi_in_config.enabled_channels):
                            continue
                        if message.type == "clock":
                            continue
                        if self.key_out_config.enabled:
                            self.message_player.play_message(message)
                    QCoreApplication.processEvents()
                    if not message:
                        time.sleep(self.MIDI_LISTEN_INTERVAL / 1000)
        except Exception as e:
            self.logger.error(f"Error in MIDI input worker: {e}")
            self.status_changed.emit(False, str(e))
        finally:
            self.running = False
            self.status_changed.emit(False, "")

    @Slot()
    def stop(self):
        self.running = False

class MidiInManager(QObject):
    # message_received = Signal(mido.Message)
    status_changed = Signal(bool, str) # status, reason

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.worker = None
        self.worker_thread = None
        self._running = False

    def start(self):
        if self.worker_thread and self.worker_thread.isRunning():
            return
        self.worker_thread = QThread()
        self.worker = MidiInWorker(self.config)
        self.worker.moveToThread(self.worker_thread)
        self.worker.status_changed.connect(self.status_changed)
        self.worker_thread.started.connect(self.worker.start)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()
        self._running = True

    def stop(self):
        if self.worker:
            self.worker.stop()

        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()

        self.worker = None
        self.worker_thread = None
        self._running = False

    @property
    def running(self):
        return self._running