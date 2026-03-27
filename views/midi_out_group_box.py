from PySide6.QtWidgets import QGroupBox
from PySide6.QtCore import Slot, QTimer
import mido
from ui.ui_midi_out_group_box import Ui_midi_out_group_box
from models import MidiOutConfig
from core import MidiOutManager
from logger import get_logger
from utils.ui_constants import UIConstants

class MidiOutGroupBox(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_midi_out_group_box()
        self.ui.setupUi(self)
        self.config = None
        self.manager = None
        self.logger = get_logger(__name__)
        self._init_connection()
        self._init_timer()
        self.update_device_list()

    def _init_connection(self):
        self.ui.device_list_widget.itemSelectionChanged.connect(self.update_config)
        self.ui.enable_check_box.stateChanged.connect(self._handle_enabled_changed)
        self.ui.clear_selection_push_button.clicked.connect(self.ui.device_list_widget.clearSelection)
        self.ui.refresh_push_button.clicked.connect(self.update_device_list)
        self.ui.merge_channel_group_box.toggled.connect(self.update_config)
        self.ui.target_channel_spin_box.valueChanged.connect(self.update_config)
    
    def _init_timer(self):
        self.device_update_timer = QTimer(parent=self, interval=UIConstants.midi_device_update_interval)
        self.device_update_timer.timeout.connect(self.update_device_list)
        self.device_update_timer.start()

    def load(self, config: MidiOutConfig) -> None:
        self.config = config
        self.manager = MidiOutManager(config, parent=self)
        self.manager.status_changed.connect(self._handle_manager_status_changed)
        self.update_ui()

    @Slot(mido.Message)
    def send_message(self, message: mido.Message):
        if self.manager and self.config.enabled:
            self.manager.send_message(message)

    @Slot()
    def update_device_list(self):
        self.device_names = mido.get_output_names()
        self.ui.device_list_widget.blockSignals(True)
        self.ui.device_list_widget.clear()
        self.ui.device_list_widget.addItems(self.device_names)
        if self.config:
            self._update_device_selection()
        self.ui.device_list_widget.blockSignals(False)

    def _update_device_selection(self):
        if not self.config.device_name:
            self.ui.device_list_widget.setCurrentRow(-1)
            return
        for i in range(self.ui.device_list_widget.count()):
            item = self.ui.device_list_widget.item(i)
            if item.text() == self.config.device_name:
                item.setSelected(True)
                break
        else:
            self.logger.warning(f"Selected MIDI output device '{self.config.device_name}' not found")
            self.config.device_name = ""
            self.ui.device_list_widget.setCurrentRow(-1)
            if self.manager and self.manager.running:
                self.ui.enable_check_box.setChecked(False)

    @Slot()
    def update_ui(self):
        if self.config:
            self._update_device_selection()
            self.ui.enable_check_box.blockSignals(True)
            self.ui.enable_check_box.setChecked(self.config.enabled)
            self.ui.enable_check_box.blockSignals(False)
            self.ui.merge_channel_group_box.blockSignals(True)
            self.ui.merge_channel_group_box.setChecked(self.config.merge_channels)
            self.ui.merge_channel_group_box.blockSignals(False)
            self.ui.target_channel_spin_box.blockSignals(True)
            self.ui.target_channel_spin_box.setValue(self.config.target_channel + 1)
            self.ui.target_channel_spin_box.blockSignals(False)

    @Slot()
    def update_config(self):
        if self.config:
            selected_items = self.ui.device_list_widget.selectedItems()
            if selected_items:
                self.config.device_name = selected_items[0].text()
                self.ui.enable_check_box.setEnabled(True)
            else:
                self.config.device_name = ""
                self.ui.enable_check_box.setEnabled(False)
                # self.logger.debug("No MIDI output device selected")
            self.config.enabled = self.ui.enable_check_box.isChecked()
            self.config.merge_channels = self.ui.merge_channel_group_box.isChecked()
            self.config.target_channel = self.ui.target_channel_spin_box.value() - 1

    @Slot(bool)
    def _handle_enabled_changed(self, enabled: bool):
        self.update_config()  # sync config with UI
        if self.manager:
            if enabled:
                self.manager.start()
                self.ui.device_list_widget.setEnabled(False)
                self.ui.refresh_push_button.setEnabled(False)
                self.ui.clear_selection_push_button.setEnabled(False)
            else:
                self.manager.stop()
                self.ui.device_list_widget.setEnabled(True)
                self.ui.refresh_push_button.setEnabled(True)
                self.ui.clear_selection_push_button.setEnabled(True)
        else:
            self.logger.error("MIDI output config not loaded. Cannot start MIDI output manager")

    @Slot(bool, str)
    def _handle_manager_status_changed(self, running: bool, reason: str):
        if len(reason) > 0:
            if running:
                self.logger.info(f"MIDI output started because: {reason}")
            else:
                self.logger.warning(f"MIDI output stopped unexpectedly because: {reason}")
            # sync to config
            if self.config:
                self.config.enabled = running
                self.update_ui()
        else:
            if running:
                self.logger.info("MIDI output started successfully")
            else:
                self.logger.info("MIDI output stopped")

    def closeEvent(self, event):
        if self.manager:
            self.manager.stop()
        return super().closeEvent(event)

            