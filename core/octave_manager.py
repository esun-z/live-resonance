from typing import Tuple
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from utils.system_utils import press_and_release_key, press_key, release_key
from utils.midi_utils import get_note_octave
from utils.ui_constants import UIConstants
from models.key_map_config import KeyMapConfig
from logger import get_logger

class Offsets:
    vision_octave_count = UIConstants.vision_octave_count
    def __init__(self, vision_offset: int, octave_offset: int, vision_base_octave: int):
        self.vision_offset = vision_offset
        self.octave_offset = octave_offset
        self.vision_base_octave = vision_base_octave

    def get_vision_octave_range(self) -> range:
        min_octave = self.vision_base_octave + self.octave_offset + self.vision_offset * self.vision_octave_count
        return range(min_octave, min_octave + self.vision_octave_count)
    
    def get_vision_note_range(self) -> range:
        octave_range = self.get_vision_octave_range()
        return range(octave_range.start * 12, octave_range.stop * 12)
    
    def is_note_in_vision(self, note: int) -> bool:
        return get_note_octave(note) in self.get_vision_octave_range()
    
    def get_key_index_by_note(self, note: int) -> int:
        note_range = self.get_vision_note_range()
        if note in note_range:
            return note - note_range.start
        else:
            return -1
    
    @classmethod
    def from_octave(cls, start_octave: int, vision_base_octave: int) -> 'Offsets':
        rel_octave = start_octave - vision_base_octave
        vision_offset = (rel_octave + 1) // cls.vision_octave_count
        octave_offset = rel_octave % cls.vision_octave_count
        if octave_offset > 1:
            octave_offset -= cls.vision_octave_count
        return cls(vision_offset, octave_offset, vision_base_octave)
    
    def get_nearest_offsets_to_cover_octave(self, octave: int) -> 'Offsets':
        if octave in self.get_vision_octave_range():
            return Offsets(self.vision_offset, self.octave_offset, self.vision_base_octave)
        else:
            if octave < self.get_vision_octave_range().start:
                target_start_octave = octave
            else: # octave >= current_octave_range.stop
                target_start_octave = octave - self.vision_octave_count + 1
            return Offsets.from_octave(target_start_octave, self.vision_base_octave)

class OctaveManager(QObject):
    move_finished = Signal()
    octave_switch_duration = 60
    def __init__(self, key_map_config: KeyMapConfig, switch_cooldown_ms: int, vision_base_octave: int, parent=None) -> None:
        super().__init__(parent)
        self.vision_base_octave = vision_base_octave
        self.offsets = Offsets(0, 0, vision_base_octave)
        self.next_offsets = Offsets(0, 0, vision_base_octave)
        self.key_map_config = key_map_config
        self.is_switching_octave = False
        self.is_cooldown = False
        self.octave_switch_cooldown_ms = switch_cooldown_ms
        self._last_move_has_octave_up = False
        # self.logger = get_logger(__name__)
    
    def move_to_offsets(self, target_offsets: Offsets) -> bool:
        if self.is_switching_octave or self.is_cooldown:
            return False
        moved = False
        # move octave offset
        if target_offsets.octave_offset != self.offsets.octave_offset:
            moved = True
            if target_offsets.octave_offset == -1:
                if self.offsets.vision_offset == -1: # cannot move to (-1, -1)
                    moved = False
                else:
                    press_and_release_key(self.key_map_config.octave_low_offset_switch)
            elif target_offsets.octave_offset == 1:
                if self.offsets.vision_offset == 1: # cannot move to (1, 1)
                    moved = False
                else:
                    press_key(self.key_map_config.octave_high_offset_switch)
                    self._last_move_has_octave_up = True
                    # deal with release after duration for target process to recognize the octave switch
            else: # target_octave_offset == 0
                if self.offsets.octave_offset < 0:
                    press_and_release_key(self.key_map_config.octave_low_offset_switch) # press low offset again to cancel low offset
                elif self.offsets.octave_offset > 0:
                    press_key(self.key_map_config.octave_high_offset_switch) # press high offset again to cancel high offset
                    self._last_move_has_octave_up = True
                else: # should not happen
                    raise ValueError(f"Invalid target octave offset {target_offsets.octave_offset} when current octave offset is {self.offsets.octave_offset}")
            
        # move vision offset
        if target_offsets.vision_offset != self.offsets.vision_offset:
            moved = True
            if target_offsets.vision_offset < 0:
                press_and_release_key(self.key_map_config.vision_to_low)
            elif target_offsets.vision_offset == 0:
                press_and_release_key(self.key_map_config.vision_to_mid)
            else: # target_vision_offset > 0
                press_and_release_key(self.key_map_config.vision_to_high)
        
        if moved:
            self.is_switching_octave = True
            self.next_offsets = target_offsets
            QTimer.singleShot(self.octave_switch_duration, self._handle_move_finished)

    def _handle_move_finished(self):
        if self._last_move_has_octave_up:
            release_key(self.key_map_config.octave_high_offset_switch)
            self._last_move_has_octave_up = False
        self.offsets = self.next_offsets
        self.is_switching_octave = False
        self.move_finished.emit()
        QTimer.singleShot(self.octave_switch_cooldown_ms, self.reset_cooldown)

    def reset_cooldown(self) -> None:
        self.is_cooldown = False

    def reset_octaves(self, with_key_output: bool = False) -> None:
        if with_key_output:
            self.move_to_offsets(Offsets(0, 0, self.vision_base_octave))
        else:
            self.offsets = Offsets(0, 0, self.vision_base_octave)
            self.next_offsets = Offsets(0, 0, self.vision_base_octave)

    def move_to_cover_note(self, note: int) -> bool:
        note_octave = get_note_octave(note)
        target_offsets = self.offsets.get_nearest_offsets_to_cover_octave(note_octave)
        return self.move_to_offsets(target_offsets)
    
    def get_key_index_by_note(self, note: int) -> int:
        return self.offsets.get_key_index_by_note(note)
    
    @property
    def vision_octave_count(self) -> int:
        return self.offsets.vision_octave_count

# class OctaveManager(QObject):
#     vision_octave_count = UIConstants.vision_octave_count
#     # vision_base_octave = 4
#     octave_switch_key_down_ms = 30
#     interval_between_octave_and_vision_switch_ms = 10
#     def __init__(self, key_map_config: KeyMapConfig, switch_cooldown_ms: int, vision_base_octave: int, parent=None):
#         super().__init__(parent)
#         self.octave_offset = 0
#         self.vision_offset = 0
#         self.key_map_config = key_map_config
#         self.vision_base_octave = vision_base_octave
#         self.is_switching_octave = False
#         self.is_cooldown = False
#         self.octave_switch_cooldown_ms = switch_cooldown_ms
#         self.logger = get_logger(__name__)

#     def get_vision_octave_range(self) -> range:
#         min_octave = self.vision_base_octave + self.octave_offset + self.vision_offset * self.vision_octave_count
#         return range(min_octave, min_octave + self.vision_octave_count)
    
#     def get_offsets_from_octave(self, start_octave: int) -> Tuple[int, int]:
#         rel_octave = start_octave - self.vision_base_octave
#         vision_offset = (rel_octave + 1) // self.vision_octave_count
#         octave_offset = rel_octave % self.vision_octave_count
#         if octave_offset > 1:
#             octave_offset -= self.vision_octave_count
#         return vision_offset, octave_offset

#     def get_nearest_octave_range_to_cover_octave(self, octave: int) -> Tuple[int, int]:
#         current_octave_range = self.get_vision_octave_range()
#         if octave in current_octave_range:
#             return self.vision_offset, self.octave_offset
#         else:
#             if octave < current_octave_range.start:
#                 target_start_octave = octave
#             else: # octave >= current_octave_range.stop
#                 target_start_octave = octave - self.vision_octave_count + 1
#             return self.get_offsets_from_octave(target_start_octave)

    
#     def to_note_range(self) -> range:
#         octave_range = self.get_vision_octave_range()
#         return range(octave_range.start * 12, octave_range.stop * 12)

#     def is_move_available(self, move_offset: int) -> bool:
#         return abs(self.vision_offset * self.vision_octave_count + self.octave_offset + move_offset) <= 3
    
#     def _move_octave_offset(self, target_octave_offset: int) -> bool:
#         moved = False
#         if target_octave_offset != self.octave_offset:
#             moved = True
#             if target_octave_offset == -1:
#                 if self.vision_offset == -1: # cannot move to (-1, -1)
#                     moved = False
#                 else:
#                     self._octave_offset_shift(self.key_map_config.octave_low_offset_switch, target_octave_offset)
#                 self.logger.debug(f"Moved octave offset down to {target_octave_offset}")
#             elif target_octave_offset == 1:
#                 if self.vision_offset == 1: # cannot move to (1, 1)
#                     moved = False
#                 else:
#                     self._octave_offset_shift(self.key_map_config.octave_high_offset_switch, target_octave_offset)
#                 self.logger.debug(f"Moved octave offset up to {target_octave_offset}")
#             else: # target_octave_offset == 0
#                 if self.octave_offset < 0:
#                     self._octave_offset_shift(self.key_map_config.octave_low_offset_switch, target_octave_offset) # press low offset again to cancel low offset
#                 elif self.octave_offset > 0:
#                     self._octave_offset_shift(self.key_map_config.octave_high_offset_switch, target_octave_offset) # press high offset again to cancel high offset
#                 else: # should not happen
#                     raise ValueError(f"Invalid target octave offset {target_octave_offset} when current octave offset is {self.octave_offset}")
#                 self.logger.debug(f"Reset octave offset to {target_octave_offset}")
#             # self.octave_offset = target_octave_offset
#         return moved
    
#     def _move_vision_offset(self, target_vision_offset: int) -> bool:
#         moved = False
#         if target_vision_offset != self.vision_offset:
#             moved = True
#             if target_vision_offset < 0:
#                 press_and_release_key(self.key_map_config.vision_to_low)
#             elif target_vision_offset == 0:
#                 press_and_release_key(self.key_map_config.vision_to_mid)
#             else: # target_vision_offset > 0
#                 press_and_release_key(self.key_map_config.vision_to_high)
#             self.vision_offset = target_vision_offset
#         return moved
    
#     def move_to_offset(self, target_vision_offset: int, target_octave_offset: int) -> bool:
#         if self.is_switching_octave or self.is_cooldown:
#             return False
#         # move vision offset first to prevent edging circumstances
#         moved = self._move_vision_offset(target_vision_offset)
#         # then move octave offset
#         QTimer.singleShot(self.interval_between_octave_and_vision_switch_ms, lambda: self._move_octave_offset(target_octave_offset))
#         if target_octave_offset != self.octave_offset and not (target_octave_offset == -1 and self.vision_offset == -1) and not (target_octave_offset == 1 and self.vision_offset == 1):
#             moved = True
#         # moved = False
#         # if target_octave_offset != self.octave_offset:
#         #     moved = True
#         #     if target_octave_offset == -1:
#         #         self._octave_offset_shift(self.key_map_config.octave_low_offset_switch, target_octave_offset)
#         #         self.logger.debug(f"Moved octave offset down to {target_octave_offset}")
#         #     elif target_octave_offset == 1:
#         #         # press_and_release_key(self.key_map_config.octave_high_offset_switch)
#         #         self._octave_offset_shift(self.key_map_config.octave_high_offset_switch, target_octave_offset)
#         #         self.logger.debug(f"Moved octave offset up to {target_octave_offset}")
#         #     else: # target_octave_offset == 0
#         #         if self.octave_offset < 0:
#         #             self._octave_offset_shift(self.key_map_config.octave_low_offset_switch, target_octave_offset) # press low offset again to cancel low offset
#         #         elif self.octave_offset > 0:
#         #             # press_and_release_key(self.key_map_config.octave_high_offset_switch) # press high offset again to cancel high offset
#         #             self._octave_offset_shift(self.key_map_config.octave_high_offset_switch, target_octave_offset)
#         #         else: # should not happen
#         #             raise ValueError(f"Invalid target octave offset {target_octave_offset} when current octave offset is {self.octave_offset}")
#         #         self.logger.debug(f"Reset octave offset to {target_octave_offset}")
#         #     self.octave_offset = target_octave_offset
#         # # move vision offset
#         # if target_vision_offset != self.vision_offset:
#         #     moved = True
#         #     if target_vision_offset < 0:
#         #         press_and_release_key(self.key_map_config.vision_to_low)
#         #     elif target_vision_offset == 0:
#         #         press_and_release_key(self.key_map_config.vision_to_mid)
#         #     else: # target_vision_offset > 0
#         #         press_and_release_key(self.key_map_config.vision_to_high)
#         #     self.vision_offset = target_vision_offset
#         if moved:
#             self.is_cooldown = True
#             QTimer.singleShot(self.octave_switch_cooldown_ms, self._reset_cooldown)
#         return moved
    
#     def _octave_offset_shift(self, key: str, target_octave_offset: int):
#         press_key(key)
#         self.is_switching_octave = True
#         QTimer.singleShot(self.octave_switch_key_down_ms, lambda: self._handle_octave_offset_shift_timeout(key, target_octave_offset))

#     @Slot(str, int)
#     def _handle_octave_offset_shift_timeout(self, key: str, target_octave_offset: int):
#         release_key(key)
#         self.is_switching_octave = False
#         self.octave_offset = target_octave_offset
    
#     @Slot()
#     def _reset_cooldown(self):
#         self.is_cooldown = False

#     def move_to_cover_note(self, note: int) -> bool:
#         note_octave = get_note_octave(note)
#         target_vision_offset, target_octave_offset = self.get_nearest_octave_range_to_cover_octave(note_octave)
#         self.logger.debug(f"Moving octave to cover note {note} with target vision offset {target_vision_offset} and target octave offset {target_octave_offset}")
#         return self.move_to_offset(target_vision_offset, target_octave_offset)

#     def get_key_index_by_note(self, note: int) -> int:
#         note_range = self.to_note_range()
#         if note in note_range:
#             return note - note_range.start
#         else:
#             return -1
    
    # def get_move_notes(self, move_offset: int) -> List[OctaveMoveNote]:
    #     if move_offset == 0 or not self.is_move_available(move_offset):
    #         return []
    #     # check if octave offset could apply
    #     in_vision_move_offset = self.octave_offset + move_offset
    #     if in_vision_move_offset == 0:
    #         if self.octave_offset == -1:
    #             return [OctaveMoveNote.offset_down] # cancel down offset
    #         elif self.octave_offset == 1:
    #             return [OctaveMoveNote.offset_up] # cancel up offset
    #         else: # should not happen
    #             return []
    #     elif in_vision_move_offset == -1:
    #         return [OctaveMoveNote.offset_down] # move down
    #     elif in_vision_move_offset == 1:
    #         return [OctaveMoveNote.offset_up] # move up
    #     else: # unable to move in vision, need cross vision movement
    #         seq = []
    #         if abs(in_vision_move_offset) == 2:
                


    
if __name__ == "__main__":
    manager = OctaveManager()
    print(manager.get_vision_octave_range())
    print(manager.is_move_available(3))
    print(manager.is_move_available(4))
    for i in range(9):
        print(manager.get_offsets_from_octave(i))