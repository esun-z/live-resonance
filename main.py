from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLocale
import sys
import ctypes
import os
from main_window import MainWindow
from utils.system_utils import is_admin, resource_path

def main():
    # Check if the application is running as an administrator
    if not is_admin():
        # Relaunch the application with elevated privileges
        params = " ".join(sys.argv)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)  # Exit the current process

    # Continue with the application if already running as admin
    app = QApplication(sys.argv)

    locale = QLocale.system().name()
    if locale.startswith("zh"):
        translator = QTranslator()
        qm_file = resource_path(os.path.join("i18n", "zh_CN.qm"))
        if translator.load(qm_file):
            app.installTranslator(translator)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()