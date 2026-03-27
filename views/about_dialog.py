# about_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
import os
import sys
from utils.system_utils import resource_path
from utils.ui_constants import UIConstants

def get_license_text():
    license_path = resource_path("LICENSE")
    if os.path.exists(license_path):
        with open(license_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "See https://www.gnu.org/licenses/gpl-3.0.html"
    
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {UIConstants.project_name}")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        title_label = QLabel(f"<h1>{UIConstants.project_name}</h1>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        license_text = get_license_text()
        license_edit = QTextEdit()
        license_edit.setReadOnly(True)
        license_edit.setPlainText(license_text)
        layout.addWidget(license_edit)

        button_layout = QHBoxLayout()
        github_button = QPushButton("GitHub")
        github_button.clicked.connect(self.open_github)
        button_layout.addWidget(github_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def open_github(self):
        url = QUrl(UIConstants.github_url)
        QDesktopServices.openUrl(url)