from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QStackedWidget
import os
import sys


class MainWidget(QStackedWidget):
    closed = pyqtSignal()

    def __init__(self):
        super(MainWidget, self).__init__()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.closed.emit()

    def silent_reload(self):
        os.execl(sys.executable, sys.executable, *sys.argv)
