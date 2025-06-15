# settings.py
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.layout = QVBoxLayout(self)

        # Dark Mode checkbox
        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.dark_mode_checkbox.setChecked(self.is_dark_mode_enabled())
        self.layout.addWidget(self.dark_mode_checkbox)

        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_settings(self):
        # Toggle dark mode based on checkbox state
        if self.dark_mode_checkbox.isChecked():
            self.set_dark_mode(True)
        else:
            self.set_dark_mode(False)
        self.accept()

    def set_dark_mode(self, enable):
        app = QApplication.instance()
        palette = QPalette()

        if enable:
            palette.setColor(QPalette.Background, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        else:
            palette.setColor(QPalette.Background, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, QColor(0, 0, 0))

        app.setPalette(palette)
        self.parent().set_dark_mode(enable)  # Propagate to Browser

    def is_dark_mode_enabled(self):
        app_palette = QApplication.instance().palette()
        return app_palette.color(QPalette.Background) == QColor(53, 53, 53)  # Dark mode detection
