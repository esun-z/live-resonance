# from utils.system_utils import press_key, release_key
from models import KeyMapConfig
from .keyboard_manager import KeyboardManager

class NoteManager:
    def __init__(self, key_map_config: KeyMapConfig, keyboard_manager: KeyboardManager):
        self.key_map_config = key_map_config
        self.vision_size = len(key_map_config.notes)
        self.key_status = [False] * self.vision_size
        self._keyboard = keyboard_manager

    def play_note(self, note: int, is_on: bool, disable_allow_repeat: bool = False) -> bool:
        played = False
        if 0 <= note < self.vision_size:
            if self.key_status[note] != is_on:
                key = self.key_map_config.notes[note]
                if is_on:
                    self._keyboard.press_key(key)
                else:
                    self._keyboard.release_key(key)
                self.key_status[note] = is_on
                played = True
            else:
                if self.key_map_config.allow_repeat and is_on and not disable_allow_repeat:
                    key = self.key_map_config.notes[note]
                    self._keyboard.release_key(key)
                    self._keyboard.press_key(key)
                    played = True
        return played
    
    def release_all_notes(self):
        for note, is_on in enumerate(self.key_status):
            if is_on:
                key = self.key_map_config.notes[note]
                self._keyboard.release_key(key)
                self.key_status[note] = False