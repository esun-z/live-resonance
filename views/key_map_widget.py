from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot
from .piano_widget import PianoWidget
from ui.ui_key_map_widget import Ui_key_map_widget
from models import KeyMapConfig, PlayerConfig
from utils.ui_constants import UIConstants
from utils.midi_utils import get_note_name

class KeyMapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_key_map_widget()
        self.ui.setupUi(self)
        self.key_map = None
        self.player_config = None
        self.ui.piano_widget.setFixedHeight(UIConstants.white_key_height)
        self.ui.piano_widget.selected_changed.connect(self._handle_selected_note_changed)
        self._init_connection()

    def load(self, key_map_config: KeyMapConfig, player_config: PlayerConfig):
        self.key_map = key_map_config
        self.player_config = player_config
        self.ui.piano_widget.load(key_map_config, player_config.vision_base_octave)
        self.update_ui()

    def _init_connection(self):
        # octave offset
        self.ui.octave_up_line_edit.editingFinished.connect(self.update_config_control_keys)
        self.ui.octave_down_line_edit.editingFinished.connect(self.update_config_control_keys)
        # vision switch
        self.ui.vision_high_line_edit.editingFinished.connect(self.update_config_control_keys)
        self.ui.vision_mid_line_edit.editingFinished.connect(self.update_config_control_keys)
        self.ui.vision_low_line_edit.editingFinished.connect(self.update_config_control_keys)
        # sustain
        self.ui.sustain_line_edit.editingFinished.connect(self.update_config_control_keys)
        # allow repeat
        self.ui.allow_repeat_check_box.stateChanged.connect(self.update_config_control_keys)
        # note key
        self.ui.note_key_line_edit.editingFinished.connect(self.update_config_note_key)

    @Slot(int)
    def _handle_selected_note_changed(self, key_index: int):
        self.ui.note_key_line_edit.blockSignals(True)
        if key_index >= 0:
            current_key = self.key_map.notes[key_index] if self.key_map and key_index < len(self.key_map.notes) else ""
            self.ui.note_key_line_edit.setText(current_key)
            note_num = self.ui.piano_widget.get_selected_note()
            self.ui.note_label.setText(f"{get_note_name(note_num, is_musical=True)}({note_num})")
        else:
            self.ui.note_key_line_edit.setText("")
            self.ui.note_label.setText("")
        self.ui.note_key_line_edit.blockSignals(False)

    @Slot()
    def update_ui(self):
        if not isinstance(self.sender(), PianoWidget) and self.player_config:
            self.ui.piano_widget.base_octave = self.player_config.vision_base_octave
            self.ui.piano_widget.update_ui()
        # current key if selected
        self._handle_selected_note_changed(self.ui.piano_widget.selected_key_index)
        if self.key_map:
            # octave offset
            self.ui.octave_up_line_edit.blockSignals(True)
            self.ui.octave_up_line_edit.setText(self.key_map.octave_high_offset_switch)
            self.ui.octave_up_line_edit.blockSignals(False)
            self.ui.octave_down_line_edit.blockSignals(True)
            self.ui.octave_down_line_edit.setText(self.key_map.octave_low_offset_switch)
            self.ui.octave_down_line_edit.blockSignals(False)
            # vision switch
            self.ui.vision_high_line_edit.blockSignals(True)
            self.ui.vision_high_line_edit.setText(self.key_map.vision_to_high)
            self.ui.vision_high_line_edit.blockSignals(False)
            self.ui.vision_mid_line_edit.blockSignals(True)
            self.ui.vision_mid_line_edit.setText(self.key_map.vision_to_mid)
            self.ui.vision_mid_line_edit.blockSignals(False)
            self.ui.vision_low_line_edit.blockSignals(True)
            self.ui.vision_low_line_edit.setText(self.key_map.vision_to_low)
            self.ui.vision_low_line_edit.blockSignals(False)
            # sustain
            self.ui.sustain_line_edit.blockSignals(True)
            self.ui.sustain_line_edit.setText(self.key_map.sustain)
            self.ui.sustain_line_edit.blockSignals(False)
            # allow repeat
            self.ui.allow_repeat_check_box.blockSignals(True)
            self.ui.allow_repeat_check_box.setChecked(self.key_map.allow_repeat)
            self.ui.allow_repeat_check_box.blockSignals(False)

    @Slot()
    def update_config_control_keys(self):
        if self.key_map:
            # octave offset
            self.key_map.octave_high_offset_switch = self.ui.octave_up_line_edit.text()
            self.key_map.octave_low_offset_switch = self.ui.octave_down_line_edit.text()
            # vision switch
            self.key_map.vision_to_high = self.ui.vision_high_line_edit.text()
            self.key_map.vision_to_mid = self.ui.vision_mid_line_edit.text()
            self.key_map.vision_to_low = self.ui.vision_low_line_edit.text()
            # sustain
            self.key_map.sustain = self.ui.sustain_line_edit.text()
            # allow repeat
            self.key_map.allow_repeat = self.ui.allow_repeat_check_box.isChecked()

    @Slot()
    def update_config_note_key(self):
        new_key = self.ui.note_key_line_edit.text()
        if self.key_map and 0 <= self.ui.piano_widget.selected_key_index < len(self.key_map.notes):
            self.key_map.notes[self.ui.piano_widget.selected_key_index] = new_key
            self.ui.piano_widget.update_ui()
