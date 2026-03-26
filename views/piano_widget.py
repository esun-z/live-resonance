from PySide6.QtWidgets import QWidget

from utils.ui_constants import UIConstants
from utils.midi_utils import get_note_name
from .piano_key_button import PianoKeyButton

class PianoWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.selected_note = None
        self.key_buttons = []
        
        # create key buttons for 3 octaves
        for octave in range(3):
            for note in range(12):
                note_number = octave * 12 + note
                note_name = get_note_name(note_number, is_musical=True)
                is_black = '#' in note_name
                key_button = PianoKeyButton(note_name=note_name, key_name='', is_black=is_black, parent=self)
                self.key_buttons.append(key_button)
