from PySide6.QtCore import QObject, QTimer
from utils.system_utils import press_and_release_key
from collections import deque
from typing import Callable, Any

# class SustainManager(QObject):
#     def __init__(self, key_map_config: KeyMapConfig, parent=None):
#         super().__init__(parent=parent)
#         self.key_map_config = key_map_config
#         self.sustain_on = False

    
    
#     def _set_sustain(self, is_on: bool) -> None:
#         if is_on != self.sustain_on:
#             press_and_release_key(self.key_map_config.sustain)
#         self.sustain_on = is_on

class SustainManager(QObject):
    def __init__(self, min_interval: int, padel_key: str, parent: QObject = None):
        super().__init__(parent)
        self._padel_key = padel_key
        self._min_interval = min_interval
        self._queue = deque()
        self._is_padel_pressed = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._process_next)

        self._is_running = False

    def submit(self, is_on: bool) -> None:
        self._queue.append(is_on)
        if not self._is_running:
            # if not currently running, start processing the queue
            self._process_next()

    def _process_next(self):
        if not self._queue:
            self._is_running = False
            return

        # execute the first task in the queue
        is_on = self._queue.popleft()
        if is_on != self._is_padel_pressed:
            press_and_release_key(self._padel_key)
            self._is_padel_pressed = is_on

        # set timer for the next task
        self._is_running = True
        self._timer.start(self._min_interval)