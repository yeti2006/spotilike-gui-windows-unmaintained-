import sys, os
import logging as log
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox


class messageBox(QMessageBox):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        log.warning("Quitting application")
        quit()


def error_box(error: Exception):
    msg = messageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Mission failed successfully")
    msg.setInformativeText(f"Error type:\n{error.__class__.__name__}")
    msg.setWindowTitle("SpotiLike err :(")
    msg.setDetailedText(f"The full exception is as follows:\n\n{error}")

    msg.exec_()


class UncaughtHook(QObject):
    """Emits a signal to _ everytime an unhandled exception is raised"""

    _exception_caught = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        sys.excepthook = self.exception_hook

    def exception_hook(self, exc_type, exc_value, exc_traceback):

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        else:
            exc_info = (exc_type, exc_value, exc_traceback)
            log_msg = f"{exc_type.__name__}: {exc_value}"
            log.critical("Uncaught exception:\n {0}".format(log_msg), exc_info=exc_info)

            self._exception_caught.emit(log_msg)
