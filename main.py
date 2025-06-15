# main.py
import sys
from PyQt5.QtWidgets import QApplication
from browser import Browser

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Python Web Browser")
    window = Browser()
    window.show()
    sys.exit(app.exec_())
