
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QStackedWidget
import os
import sys
# os.chdir(os.getcwd()+"\\Spotike 2.0")

class MainWidget(QStackedWidget):
    closed = pyqtSignal()
    def __init__(self):
        super(MainWidget, self).__init__()
        
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.closed.emit()
        self.silent_reload()
        
    def silent_reload(self):
        os.execl(sys.executable, sys.executable, * sys.argv)