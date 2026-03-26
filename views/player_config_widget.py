from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, Slot
from ui.ui_player_config_widget import Ui_player_config_widget
from models import PlayerConfig, OutOfRangeStrategy, OctaveStrategy

class PlayerConfigWidget(QWidget):
    base_octave_changed = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_player_config_widget()
        self.ui.setupUi(self)
        self.config = None
        self._init_ui()
        self._init_connection()

    def load(self, config: PlayerConfig):
        self.config = config
        self.update_ui()

    def _init_ui(self):
        self.ui.high_out_of_range_strategy_combo_box.clear()
        self.ui.low_out_of_range_strategy_combo_box.clear()
        for strategy in OutOfRangeStrategy:
            self.ui.high_out_of_range_strategy_combo_box.addItem(strategy.value)
            self.ui.low_out_of_range_strategy_combo_box.addItem(strategy.value)
        self.ui.octave_strategy_combo_box.clear()
        for strategy in OctaveStrategy:
            self.ui.octave_strategy_combo_box.addItem(strategy.value)

    def _init_connection(self):
        self.ui.min_note_spin_box.valueChanged.connect(self.update_config)
        self.ui.max_note_spin_box.valueChanged.connect(self.update_config)
        self.ui.vision_base_octave_spin_box.valueChanged.connect(self.update_config)
        self.ui.high_out_of_range_strategy_combo_box.currentTextChanged.connect(self.update_config)
        self.ui.low_out_of_range_strategy_combo_box.currentTextChanged.connect(self.update_config)
        self.ui.octave_strategy_combo_box.currentTextChanged.connect(self.update_config)
        self.ui.clean_switch_check_box.stateChanged.connect(self.update_config)
        self.ui.note_after_octave_switch_ms_spin_box.valueChanged.connect(self.update_config)
        self.ui.min_padel_interval_ms_spin_box.valueChanged.connect(self.update_config)
        self.ui.octave_switch_cooldown_ms_spin_box.valueChanged.connect(self.update_config)

    @Slot()
    def update_ui(self):
        if self.config:
            # range
            self.ui.min_note_spin_box.blockSignals(True)
            self.ui.min_note_spin_box.setValue(self.config.min_note)
            self.ui.min_note_spin_box.blockSignals(False)
            self.ui.max_note_spin_box.blockSignals(True)
            self.ui.max_note_spin_box.setValue(self.config.max_note)
            self.ui.max_note_spin_box.blockSignals(False)
            self.ui.vision_base_octave_spin_box.blockSignals(True)
            self.ui.vision_base_octave_spin_box.setValue(self.config.vision_base_octave - 1) # MIDI to musical
            self.ui.vision_base_octave_spin_box.blockSignals(False)
            # strategy
            self.ui.high_out_of_range_strategy_combo_box.blockSignals(True)
            self.ui.high_out_of_range_strategy_combo_box.setCurrentText(self.config.high_out_of_range_strategy.value)
            self.ui.high_out_of_range_strategy_combo_box.blockSignals(False)
            self.ui.low_out_of_range_strategy_combo_box.blockSignals(True)
            self.ui.low_out_of_range_strategy_combo_box.setCurrentText(self.config.low_out_of_range_strategy.value)
            self.ui.low_out_of_range_strategy_combo_box.blockSignals(False)
            self.ui.octave_strategy_combo_box.blockSignals(True)
            self.ui.octave_strategy_combo_box.setCurrentText(self.config.octave_strategy.value)
            self.ui.octave_strategy_combo_box.blockSignals(False)
            self.ui.clean_switch_check_box.blockSignals(True)
            self.ui.clean_switch_check_box.setChecked(self.config.clean_switch)
            self.ui.clean_switch_check_box.blockSignals(False)
            # timing
            self.ui.note_after_octave_switch_ms_spin_box.blockSignals(True)
            self.ui.note_after_octave_switch_ms_spin_box.setValue(self.config.note_after_octave_switch_ms)
            self.ui.note_after_octave_switch_ms_spin_box.blockSignals(False)
            self.ui.min_padel_interval_ms_spin_box.blockSignals(True)
            self.ui.min_padel_interval_ms_spin_box.setValue(self.config.min_padel_interval_ms)
            self.ui.min_padel_interval_ms_spin_box.blockSignals(False)
            self.ui.octave_switch_cooldown_ms_spin_box.blockSignals(True)
            self.ui.octave_switch_cooldown_ms_spin_box.setValue(self.config.octave_switch_cooldown_ms)
            self.ui.octave_switch_cooldown_ms_spin_box.blockSignals(False)

    @Slot()
    def update_config(self):
        if self.config:
            # range
            self.config.min_note = self.ui.min_note_spin_box.value()
            self.config.max_note = self.ui.max_note_spin_box.value()
            new_base_octave = self.ui.vision_base_octave_spin_box.value() + 1 # musical to MIDI
            if self.config.vision_base_octave != new_base_octave:
                self.config.vision_base_octave = new_base_octave
                self.base_octave_changed.emit(new_base_octave)
            # strategy
            self.config.high_out_of_range_strategy = OutOfRangeStrategy(self.ui.high_out_of_range_strategy_combo_box.currentText())
            self.config.low_out_of_range_strategy = OutOfRangeStrategy(self.ui.low_out_of_range_strategy_combo_box.currentText())
            self.config.octave_strategy = OctaveStrategy(self.ui.octave_strategy_combo_box.currentText())
            self.config.clean_switch = self.ui.clean_switch_check_box.isChecked()
            # timing
            self.config.note_after_octave_switch_ms = self.ui.note_after_octave_switch_ms_spin_box.value()
            self.config.min_padel_interval_ms = self.ui.min_padel_interval_ms_spin_box.value()
            self.config.octave_switch_cooldown_ms = self.ui.octave_switch_cooldown_ms_spin_box.value()