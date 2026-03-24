from utils.system_utils import press_key, release_key
from models import KeyMapConfig

class NoteManager:
    def __init__(self, key_map_config: KeyMapConfig):
        self.key_map_config = key_map_config
        self.vision_size = len(key_map_config.notes)
        self.key_status = [False] * self.vision_size

    def play_note(self, note: int, is_on: bool, disable_allow_repeat: bool = False) -> bool:
        played = False
        if 0 <= note < self.vision_size:
            if self.key_status[note] != is_on:
                key = self.key_map_config.notes[note]
                if is_on:
                    press_key(key)
                else:
                    release_key(key)
                self.key_status[note] = is_on
                played = True
            else:
                if self.key_map_config.allow_repeat and is_on and not disable_allow_repeat:
                    key = self.key_map_config.notes[note]
                    release_key(key)
                    press_key(key)
                    played = True
        return played
    
    def release_all_notes(self):
        for note, is_on in enumerate(self.key_status):
            if is_on:
                key = self.key_map_config.notes[note]
                release_key(key)
                self.key_status[note] = False