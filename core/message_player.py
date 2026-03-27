from PySide6.QtCore import QObject, Slot, QTimer
from collections import deque
from typing import List, Tuple
import mido
from .note_manager import NoteManager
from .octave_manager import OctaveManager
from .sustain_manager import SustainManager
from utils.midi_utils import is_note_on, is_note_off, is_padel_on, is_padel_off, get_note_name, get_note_octave
from models import KeyMapConfig, PlayerConfig, OutOfRangeStrategy, OctaveStrategy
from logger import get_logger

class MessagePlayer(QObject):
    delayed_note_play_interval_ms: int = 1
    def __init__(self, key_map: KeyMapConfig, player_config: PlayerConfig, parent=None):
        super().__init__(parent)
        self.note_manager = NoteManager(key_map)
        self.octave_manager = OctaveManager(key_map_config=key_map, 
                                            switch_cooldown_ms=player_config.octave_switch_cooldown_ms, 
                                            vision_base_octave=player_config.vision_base_octave, 
                                            parent=self)
        self.octave_manager.move_finished.connect(self._handle_octave_move_finished)
        self.sustain_manager = SustainManager(min_interval=player_config.min_padel_interval_ms, 
                                            padel_key=key_map.sustain, 
                                            parent=self)
        self.player_config = player_config
        self.note_status: List[int] = [-1] * 128
        self.delayed_notes: deque[Tuple[int, int, bool]] = deque() # (original_note, note_to_play, disable_allow_repeat)
        self.delayed_releases: deque[int] = deque() # note to release after octave switch
        self._timer = None
        self._is_playing_delayed_notes = False
        self.logger = get_logger(__name__)

    @Slot()
    def reset(self):
        self.note_manager.release_all_notes()
        self.note_status = [-1] * 128
        self.delayed_notes.clear()
        self.delayed_releases.clear()
        self._is_playing_delayed_notes = False
        self._timer = None
        self.octave_manager.reset_octaves()
        self.octave_manager.reset_cooldown()
        self.sustain_manager.reset()
    
    @Slot(mido.Message)
    def play_message(self, msg: mido.Message) -> None:
        if is_note_on(msg):
            self._press_note(msg.note)
        elif is_note_off(msg):
            self._release_note(msg.note)
        elif is_padel_on(msg):
            self.sustain_manager.submit(True)
            # self.logger.debug("Padel on")
        elif is_padel_off(msg):
            self.sustain_manager.submit(False)
            # self.logger.debug("Padel off")

    def _press_note(self, note: int) -> None:
        # check note bound for out-of-range strategy
        max_bound, min_bound = None, None
        if self.player_config.octave_strategy in (OctaveStrategy.AUTO_LATCH, OctaveStrategy.LATCH_HIGH, OctaveStrategy.LATCH_LOW):
            max_bound, min_bound = self.player_config.max_note, self.player_config.min_note
        elif self.player_config.octave_strategy in (OctaveStrategy.DEFAULT_ONLY, OctaveStrategy.MANUAL):
            max_bound, min_bound = self.octave_manager.to_note_range().stop - 1, self.octave_manager.to_note_range().start
        else:
            raise NotImplementedError(f"Octave strategy {self.player_config.octave_strategy} not implemented")
        
        note_to_play = note
        disable_allow_repeat = False
        play_later = False

        if self.player_config.high_out_of_range_strategy == OutOfRangeStrategy.TO_NEAREST:
            if note > max_bound:
                note_to_play = note - (note - max_bound + 11) // 12 * 12
                disable_allow_repeat = True
        elif self.player_config.high_out_of_range_strategy == OutOfRangeStrategy.IGNORE:
            if note > max_bound:
                note_to_play = None
        else:
            raise NotImplementedError(f"Out of range strategy {self.player_config.high_out_of_range_strategy} not implemented")
        
        if self.player_config.low_out_of_range_strategy == OutOfRangeStrategy.TO_NEAREST:
            if note < min_bound:
                note_to_play = note + (min_bound - note + 11) // 12 * 12
                disable_allow_repeat = True
        elif self.player_config.low_out_of_range_strategy == OutOfRangeStrategy.IGNORE:
            if note < min_bound:
                note_to_play = None
        else:
            raise NotImplementedError(f"Out of range strategy {self.player_config.low_out_of_range_strategy} not implemented")
        
        # note in bound, check octave strategy
        if note_to_play is not None:
            key_index = self.octave_manager.get_key_index_by_note(note_to_play)
            # check if note not in current vision
            if key_index < 0:
                # if has latch strategy, try to switch octave to cover this note
                if self.player_config.octave_strategy in (OctaveStrategy.AUTO_LATCH, OctaveStrategy.LATCH_HIGH, OctaveStrategy.LATCH_LOW):
                    # check protection for high or low octaves
                    drop_by_protection = False
                    if self.player_config.octave_strategy == OctaveStrategy.LATCH_HIGH:
                        highest_playing_note = self._get_highest_playing_note()
                        if highest_playing_note >= 0:
                            highest_note_octave = get_note_octave(highest_playing_note)
                            note_to_play_octave = get_note_octave(note_to_play)
                            if highest_note_octave - note_to_play_octave >= self.octave_manager.vision_octave_count:
                                note_to_play += (highest_note_octave - note_to_play_octave - self.octave_manager.vision_octave_count + 1) * 12
                                if self.note_status[note_to_play] >= 0: # if the note after protection is still on, then drop this note
                                    drop_by_protection = True
                    elif self.player_config.octave_strategy == OctaveStrategy.LATCH_LOW:
                        lowest_playing_note = self._get_lowest_playing_note()
                        if lowest_playing_note >= 0:
                            lowest_note_octave = get_note_octave(lowest_playing_note)
                            note_to_play_octave = get_note_octave(note_to_play)
                            if note_to_play_octave - lowest_note_octave >= self.octave_manager.vision_octave_count:
                                note_to_play -= (note_to_play_octave - lowest_note_octave - self.octave_manager.vision_octave_count + 1) * 12
                                if self.note_status[note_to_play] >= 0: # if the note after protection is still on, then drop this note
                                    drop_by_protection = True

                    # do latch if note not drpped by protection
                    if not drop_by_protection:
                        if self.octave_manager.move_to_cover_note(note_to_play):
                            if self.player_config.clean_switch:
                                self.note_manager.release_all_notes() # release all notes to avoid stuck notes when switching octave
                                self.note_status = [-1] * 128 # update note status
                            play_later = True
                            # time.sleep(self.player_config.note_after_octave_switch_ms / 1000.0) # sleep after switching octave for game ui to react
                        key_index = self.octave_manager.get_key_index_by_note(note_to_play)
                elif self.player_config.octave_strategy in (OctaveStrategy.DEFAULT_ONLY, OctaveStrategy.MANUAL):
                    # warning: note out of range and this should not happen since it should have been handled by out of range strategy
                    self.logger.warning(f"Note out of range: {get_note_name(note_to_play, True)}")
                else:
                    raise NotImplementedError(f"Octave strategy {self.player_config.octave_strategy} not implemented")

                # if is switching, and the note to play is in next vision, and not in current vision, then delay the note
                if self.octave_manager.is_switching_octave and self.octave_manager.next_offsets.is_note_in_vision(note_to_play):
                    play_later = True
            
            if play_later:
                # QTimer.singleShot(self.player_config.note_after_octave_switch_ms, lambda: self._press_note_key(note, note_to_play, disable_allow_repeat))
                self.delayed_notes.append((note, note_to_play, disable_allow_repeat))
            elif 0 <= key_index < self.note_manager.vision_size:
                self._press_note_key(note, note_to_play, disable_allow_repeat)

    def _handle_octave_move_finished(self):
        if self._is_playing_delayed_notes:
            return
        if self.delayed_notes:
            self._process_next()
    
    def _process_next(self):
        if not self.delayed_notes and not self.delayed_releases:
            self._is_playing_delayed_notes = False
            return
        
        if self.delayed_notes:
            note, note_to_play, disable_allow_repeat = self.delayed_notes.popleft()
            key_index = self.octave_manager.get_key_index_by_note(note_to_play)
            if 0 <= key_index < self.note_manager.vision_size:
                self._press_note_key(note, note_to_play, disable_allow_repeat)
        elif self.delayed_releases: # only start releasing after all notes pressed
            note = self.delayed_releases.popleft()
            self._release_note(note)

        self._is_playing_delayed_notes = True
        if not self._timer:
            self._timer = QTimer(self)
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self._process_next)
        self._timer.start(self.delayed_note_play_interval_ms)
    
    @Slot(int, bool)
    def _press_note_key(self, note: int, note_to_play: int, disable_allow_repeat: bool) -> bool:
        suc = False
        key_index = self.octave_manager.get_key_index_by_note(note_to_play)
        if 0 <= key_index < self.note_manager.vision_size:
            suc = self.note_manager.play_note(note=key_index, is_on=True, disable_allow_repeat=disable_allow_repeat)
            if suc:
                self.note_status[note] = key_index
        return suc
    
    def _release_note(self, note: int) -> None:
        key_index = self.note_status[note]
        if key_index >= 0:
            self.note_manager.play_note(note=key_index, is_on=False)
            self.note_status[note] = -1
        else: # this can be caused by delayed notes.
            self.delayed_releases.append(note)
        #     if self.note_manager.play_note(note=key_index, is_on=False):
        #         self.note_status[note] = -1
        #     else:
        #         # warning: failed to release note
        #         # self.logger.warning(f"Failed to release note: {get_note_name(note, True)}")
        #         pass
        # else:
        #     # warning: note off received for a note that is not on
        #     # self.logger.warning(f"Note off received for a note that is not on: {get_note_name(note, True)}")
        #     pass

    def _get_highest_playing_note(self) -> int:
        highest_note = -1
        for note, key_index in enumerate(self.note_status):
            if key_index >= 0 and note > highest_note:
                highest_note = note
        return highest_note
    
    def _get_lowest_playing_note(self) -> int:
        lowest_note = 128
        for note, key_index in enumerate(self.note_status):
            if key_index >= 0 and note < lowest_note:
                return note
        return -1
                
        