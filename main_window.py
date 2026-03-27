from PySide6.QtWidgets import QMainWindow, QFileDialog, QMenu
from PySide6.QtCore import QSettings
from pathlib import Path
from ui.ui_main_window import Ui_main_window
from models import AppConfig
from logger import get_logger
from utils.system_utils import resource_path
from utils.ui_constants import UIConstants

class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_main_window()
        self.ui.setupUi(self)
        self._default_window_state = self.saveState()
        # self._default_geometry = self.saveGeometry()
        self.app_config = None
        self.config_path = None
        self.settings = QSettings("Star", "Band")
        self.logger = get_logger(__name__)
        self.read_settings()
        self.init_config()
        self.init_ui()
        self.load_presets()
        self.init_connection()
        self.load(self.app_config)

    def init_ui(self):
        # file menu
        file_menu = self.ui.menubar.addMenu("File")
        file_menu.addAction("Load", self.handle_load)
        file_menu.addAction("Save", self.handle_save)
        file_menu.addAction("Save As", self.handle_save_as)

        # control menu
        control_menu = self.ui.menubar.addMenu("Control")
        control_menu.addAction("Reset Player", self.handle_reset_player)

        # presets menu
        self.preset_menu = QMenu("Presets", self)
        self.ui.menubar.addMenu(self.preset_menu)
        self.ui.new_config_tool_button.setMenu(self.preset_menu)

        # views
        view_menu = self.ui.menubar.addMenu("View")
        midi_in_action = self.ui.midi_in_dock_widget.toggleViewAction()
        midi_in_action.setText("MIDI Input")
        view_menu.addAction(midi_in_action)
        out_action = self.ui.out_dock_widget.toggleViewAction()
        out_action.setText("Outputs")
        view_menu.addAction(out_action)
        log_action = self.ui.log_dock_widget.toggleViewAction()
        log_action.setText("Logs")
        view_menu.addAction(log_action)
        tool_bar_action = self.ui.menu_dock_widget.toggleViewAction()
        tool_bar_action.setText("Tools")
        view_menu.addAction(tool_bar_action)
        view_menu.addSeparator()
        view_menu.addAction("Reset View", self.reset_window_settings)
        

    def init_connection(self):
        self.ui.save_push_button.clicked.connect(self.handle_save)
        self.ui.save_as_push_button.clicked.connect(self.handle_save_as)
        self.ui.load_push_button.clicked.connect(self.handle_load)
        self.ui.reset_player_push_button.clicked.connect(self.handle_reset_player)
        # cross widget connections
        self.ui.player_config_widget.base_octave_changed.connect(self.ui.key_map_widget.update_ui)
        self.ui.midi_in_widget.message_received.connect(self.ui.out_widget.ui.midi_out_group_box.send_message)

    def read_settings(self):
        geometry = self.settings.value("MainWindow/geometry")
        window_state = self.settings.value("MainWindow/windowState")

        if geometry:
            self.restoreGeometry(geometry)

        if window_state:
            self.restoreState(window_state)

        self.config_path = self.settings.value("lastConfigPath", "", type=str)

    def write_settings(self):
        self.settings.setValue("MainWindow/geometry", self.saveGeometry())
        self.settings.setValue("MainWindow/windowState", self.saveState())
        if self.config_path:
            self.settings.setValue("lastConfigPath", self.config_path)
        self.settings.sync()

    def reset_window_settings(self):
        # self.restoreGeometry(self._default_geometry)
        self.restoreState(self._default_window_state)
        # self.settings.clear()
        # self.settings.sync()
        self.logger.info("View reset to default")

    def init_config(self):
        if self.config_path:
            try:
                config = AppConfig.load_from_yaml(self.config_path)
                if config is None:
                    raise ValueError("Invalid configuration file")
                self.app_config = config
                self.logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load configuration from {self.config_path}: {e}")
        if not self.app_config:
            self.config_path = resource_path(UIConstants.default_config_path)
            try:
                config = AppConfig.load_from_yaml(self.config_path)
                if config is None:
                    raise ValueError("Invalid configuration file")
                self.app_config = config
                self.logger.info(f"Default configuration loaded from {self.config_path}")
            except Exception as e:
                self.logger.error(f"Failed to load default configuration from {self.config_path}: {e}")
                self.app_config = AppConfig()


    def load(self, config: AppConfig) -> None:
        self.app_config = config
        self.ui.midi_in_widget.load(config)
        self.ui.out_widget.load(midi_out_config=config.midi_out, key_out_config=config.key_out)
        self.ui.key_map_widget.load(config.key_map, config.player)
        self.ui.player_config_widget.load(config.player)

    def load_presets(self):
        self.preset_menu.clear()
        preset_dir = Path(UIConstants.template_dir)
        if not preset_dir.exists():
            self.logger.warning(f"Preset directory {preset_dir} does not exist")
        else:
            for preset_file in preset_dir.glob("*.yaml"):
                action = self.preset_menu.addAction(preset_file.stem)
                action.triggered.connect(lambda checked, path=preset_file: self.load_config_file(str(path)))

    def handle_save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "YAML Files (*.yaml);;All Files (*)")
        if file_path:
            self.save_config_file(file_path)

    def handle_save(self):
        if self.config_path:
            self.save_config_file(self.config_path)
        else:
            self.handle_save_as()

    def handle_load(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "YAML Files (*.yaml);;All Files (*)")
        if file_path:
            self.load_config_file(file_path)

    def handle_reset_player(self):
        self.ui.midi_in_widget.manager.reset_player()
        self.logger.info("Player reset")
    
    def load_config_file(self, file_path: str) -> None:
        try:
            config = AppConfig.load_from_yaml(file_path)
            if config is None:
                raise ValueError("Invalid configuration file")
            self.config_path = file_path
            self.load(config)
            self.logger.info(f"Configuration loaded from {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {file_path}: {e}")

    def save_config_file(self, file_path: str) -> None:
        try:
            self.app_config.save_to_yaml(file_path)
            self.config_path = file_path
            self.logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {file_path}: {e}")

    # def handle_message(self, msg: mido.Message) -> None:
    #     # self.logger.debug(f"Received MIDI message: {msg}")
    #     self.message_player.play_message(msg)

    def closeEvent(self, event):
        self.write_settings()
        super().closeEvent(event)