from PySide6.QtWidgets import QWidget, QCheckBox
from PySide6.QtCore import QObject, Signal, Slot, QTimer
import mido
from ui.ui_midi_in_widget import Ui_midi_in_widget
from models import AppConfig
from logger import get_logger
from utils.ui_constants import UIConstants
from core import MidiInManager

class MidiInWidget(QWidget):
    # message_received = Signal(mido.Message)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_midi_in_widget()
        self.ui.setupUi(self)
        self.logger = get_logger(__name__)
        self.app_config = None
        self.config = None
        self.device_names = []
        self.manager = None
        self._init_connection()
        self._init_timer()
        self.update_device_list()

    def _init_connection(self) -> None:
        self.ui.device_list_widget.itemSelectionChanged.connect(self.update_config)
        self.ui.device_enable_check_box.stateChanged.connect(self._handle_enabled_changed)
        self.ui.clear_selection_push_button.clicked.connect(self.ui.device_list_widget.clearSelection)
        self.ui.refresh_push_button.clicked.connect(self.update_device_list)
        for i in range(16):
            checkbox_name = f"channel_check_box_{i+1}"
            checkbox = self.findChild(QCheckBox, checkbox_name)
            if checkbox:
                checkbox.stateChanged.connect(self.update_config)

    def _init_timer(self) -> None:
        self.device_update_timer = QTimer(parent=self, interval=UIConstants.midi_device_update_interval)
        self.device_update_timer.timeout.connect(self.update_device_list)
        self.device_update_timer.start()

    def load(self, config: AppConfig) -> None:
        self.app_config = config
        self.config = config.midi_in
        self.manager = MidiInManager(config, parent=self)
        # self.manager.message_received.connect(self.message_received)
        self.manager.status_changed.connect(self._handle_manager_status_changed)
        self.update_ui()

    @Slot()
    def update_device_list(self) -> None:
        self.device_names = mido.get_input_names()
        self.ui.device_list_widget.blockSignals(True)
        self.ui.device_list_widget.clear()
        self.ui.device_list_widget.addItems(self.device_names)
        if self.config:
            self._update_device_selection()
        self.ui.device_list_widget.blockSignals(False)

    def _update_device_selection(self) -> None:
        if not self.config.device_name:
            self.ui.device_list_widget.setCurrentRow(-1)
            return
        for i in range(self.ui.device_list_widget.count()):
            item = self.ui.device_list_widget.item(i)
            if item.text() == self.config.device_name:
                item.setSelected(True)
                break
        else:
            self.logger.warning(f"Selected MIDI input device '{self.config.device_name}' not found")
            self.config.device_name = ""
            self.ui.device_list_widget.setCurrentRow(-1)
            if self.manager and self.manager.running:
                self.ui.device_enable_check_box.setChecked(False)

    @Slot()
    def update_ui(self) -> None:
        if self.config:
            # update device list selection
            self._update_device_selection()
            # update enabled state
            self.ui.device_enable_check_box.blockSignals(True)
            self.ui.device_enable_check_box.setChecked(self.config.enabled)
            self.ui.device_enable_check_box.blockSignals(False)
            # update channel checkboxes
            for i in range(16):
                checkbox_name = f"channel_check_box_{i+1}"
                checkbox = self.findChild(QCheckBox, checkbox_name)
                if checkbox:
                    checkbox.blockSignals(True)
                    checkbox.setChecked(self.config.enabled_channels[i])
                    checkbox.blockSignals(False)
            # update filter
            self.ui.min_velocity_spin_box.blockSignals(True)
            self.ui.min_velocity_spin_box.setValue(self.config.min_note_velocity)
            self.ui.min_velocity_spin_box.blockSignals(False)

    @Slot()
    def update_config(self) -> None:
        if self.config:
            # update device name
            selected_items = self.ui.device_list_widget.selectedItems()
            if selected_items:
                self.config.device_name = selected_items[0].text()
                self.ui.device_enable_check_box.setEnabled(True)
            else:
                self.config.device_name = ""
                self.ui.device_enable_check_box.setEnabled(False)
                self.logger.debug("No MIDI input device selected")
            # update enabled state
            self.config.enabled = self.ui.device_enable_check_box.isChecked()
            # update channel checkboxes
            for i in range(16):
                checkbox_name = f"channel_check_box_{i+1}"
                checkbox = self.findChild(QCheckBox, checkbox_name)
                if checkbox:
                    self.config.enabled_channels[i] = checkbox.isChecked()
            # update filter
            self.config.min_note_velocity = self.ui.min_velocity_spin_box.value()

            # self.logger.debug(f"Enabled channels: {[i+1 for i, enabled in enumerate(self.config.enabled_channels) if enabled]}")

    @Slot(bool)
    def _handle_enabled_changed(self, enabled: bool) -> None:
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
            self.logger.error("MIDI input config not loaded. Cannot start MIDI input manager")

    @Slot(bool, str)
    def _handle_manager_status_changed(self, running: bool, reason: str) -> None:
        if len(reason) > 0:
            if running:
                self.logger.info(f"MIDI input started because: {reason}")
            else:
                self.logger.warning(f"MIDI input stopped unexpectedly because: {reason}")
            # sync to config
            if self.config:
                self.config.enabled = running
                self.update_ui()
        else:
            if running:
                self.logger.info("MIDI input started successfully")
            else:
                self.logger.info("MIDI input stopped")

    def closeEvent(self, event) -> None:
        if self.manager:
            self.manager.stop()
        return super().closeEvent(event)