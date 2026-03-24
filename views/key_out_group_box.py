from PySide6.QtWidgets import QGroupBox
from PySide6.QtCore import Slot
from ui.ui_key_out_group_box import Ui_key_out_group_box
from models import KeyOutConfig
from utils.ui_constants import UIConstants
from utils.system_utils import jump_to_process_window

class KeyOutGroupBox(QGroupBox):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_key_out_group_box()
        self.ui.setupUi(self)
        self.config = None
        self._init_ui()
        self._init_connection()

    def _init_ui(self):
        for process_name in UIConstants.target_process_names:
            self.ui.target_process_combo_box.addItem(process_name)

    def _init_connection(self):
        self.toggled.connect(self.update_config)
        self.ui.target_process_combo_box.currentIndexChanged.connect(self.update_config)
        self.ui.customized_check_box.stateChanged.connect(self.update_config)
        self.ui.customized_check_box.stateChanged.connect(self._handle_customized_switch)
        self.ui.customized_process_line_edit.editingFinished.connect(self.update_config)
        self.ui.auto_jump_check_box.stateChanged.connect(self.update_config)
        self.ui.jump_delay_double_spin_box.valueChanged.connect(self.update_config)
        self.ui.mute_outside_check_box.stateChanged.connect(self.update_config)
        self.ui.jump_push_button.clicked.connect(self._go_to_target_window)

    def load(self, config: KeyOutConfig) -> None:
        self.config = config
        self.update_ui()

    @Slot(bool)
    def _handle_customized_switch(self, checked: bool):
        self.ui.target_process_combo_box.setEnabled(not checked)
        self.ui.customized_process_line_edit.setEnabled(checked)

    @Slot()
    def update_ui(self):
        if self.config:
            self.blockSignals(True)
            self.setChecked(self.config.enabled)
            self.blockSignals(False)
            for i, process_name in enumerate(UIConstants.target_process_names):
                if self.config.target_process == process_name:
                    self.ui.target_process_combo_box.blockSignals(True)
                    self.ui.target_process_combo_box.setCurrentIndex(i)
                    self.ui.target_process_combo_box.blockSignals(False)
                    break
            else:
                if self.config.target_process:
                    # customized process
                    self.ui.customized_check_box.setChecked(True)
                    self.ui.customized_process_line_edit.blockSignals(True)
                    self.ui.customized_process_line_edit.setText(self.config.target_process)
                    self.ui.customized_process_line_edit.blockSignals(False)
                else:
                    # clear selection
                    self.ui.target_process_combo_box.blockSignals(True)
                    self.ui.target_process_combo_box.setCurrentIndex(-1)
                    self.ui.target_process_combo_box.blockSignals(False)
            self.ui.auto_jump_check_box.blockSignals(True)
            self.ui.auto_jump_check_box.setChecked(self.config.auto_jump)
            self.ui.auto_jump_check_box.blockSignals(False)
            self.ui.jump_delay_double_spin_box.blockSignals(True)
            self.ui.jump_delay_double_spin_box.setValue(self.config.jump_delay)
            self.ui.jump_delay_double_spin_box.blockSignals(False)
            self.ui.mute_outside_check_box.blockSignals(True)
            self.ui.mute_outside_check_box.setChecked(self.config.mute_outside_target)
            self.ui.mute_outside_check_box.blockSignals(False)

    @Slot()
    def update_config(self):
        if self.config:
            self.config.enabled = self.isChecked()
            if self.ui.customized_check_box.isChecked():
                self.config.target_process = self.ui.customized_process_line_edit.text()
            else:
                self.config.target_process = self.ui.target_process_combo_box.currentText()
            self.config.auto_jump = self.ui.auto_jump_check_box.isChecked()
            self.config.jump_delay = self.ui.jump_delay_double_spin_box.value()
            self.config.mute_outside_target = self.ui.mute_outside_check_box.isChecked()

    @Slot()
    def _go_to_target_window(self):
        if self.config:
            jump_to_process_window(self.config.target_process)