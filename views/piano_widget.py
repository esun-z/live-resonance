from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, Slot
from models import KeyMapConfig
from utils.ui_constants import UIConstants
from utils.midi_utils import get_note_name
from .piano_key_button import PianoKeyButton

class PianoWidget(QWidget):
    selected_changed = Signal(int) # selected note number, -1 for none
    white_key_positions = [0, -1, 1, -1, 2, 3, -1, 4, -1, 5, -1, 6]
    black_key_offsets = [-1, 0.7, -1, 0.8, -1, -1, 0.65, -1, 0.75, -1, 0.85, -1]
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.selected_key_index: int = -1
        self.key_buttons = []
        self.base_octave = 4
        self.key_map = None
        self.setFixedSize(UIConstants.white_key_width * 7 * UIConstants.vision_octave_count, UIConstants.white_key_height)
        
        # create key buttons for 3 octaves
        for octave in range(3):
            for note in range(12):
                is_black = self.white_key_positions[note] == -1
                key_button = PianoKeyButton(is_black=is_black, parent=self)
                # position the button
                if is_black:
                    key_button.move(octave * 7 * UIConstants.white_key_width + self.white_key_positions[note - 1] * UIConstants.white_key_width + UIConstants.white_key_width * self.black_key_offsets[note], 0)
                else:
                    key_button.move(octave * 7 * UIConstants.white_key_width + self.white_key_positions[note] * UIConstants.white_key_width, 0)
                key_button.clicked.connect(self._handle_note_selected)
                self.key_buttons.append(key_button)
        
        for button in self.key_buttons:
            if button.is_black:
                button.raise_()

        self.update_ui()

    def load(self, key_map_config: KeyMapConfig, base_octave: int) -> None:
        self.key_map = key_map_config
        self.base_octave = base_octave
        self.update_ui()

    def update_ui(self) -> None:
        for i, key_button in enumerate(self.key_buttons):
            note_number = self.base_octave * 12 + i
            prefix = "\n" * 2 if key_button.is_black else "\n" * 5
            note_name = get_note_name(note_number, is_musical=True)
            key_name = self.key_map.notes[i] if self.key_map and i < len(self.key_map.notes) else ""
            key_button.setText(f"{prefix}{note_name}\n{key_name}")

    @Slot()
    def _handle_note_selected(self):
        # get clicked button
        button = self.sender()
        if not isinstance(button, PianoKeyButton):
            self.selected_key_index = -1
        else:
            for i, key_button in enumerate(self.key_buttons):
                if key_button is button:
                    self.selected_key_index = i
                    button.update_select_status(True)
                    break
            else:
                self.selected_key_index = -1
        # update selected ui
        for i, key_button in enumerate(self.key_buttons):
            if i != self.selected_key_index:
                key_button.update_select_status(False)
        # emit signal
        self.selected_changed.emit(self.selected_key_index)

    def get_selected_note(self) -> int:
        if self.selected_key_index == -1:
            return -1
        return self.base_octave * 12 + self.selected_key_index
