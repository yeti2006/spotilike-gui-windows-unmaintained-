from cx_Freeze import setup, Executable
import sys

base = None

if sys.platform == "win32":
    base = "Win32Gui"  


executables = [Executable("SpotiLike.py", base=base, icon="icon.ico", shortcut_name="SpotiLike <3")]

packages = ["idna",
            "PyQt5.QtWidgets",
                                # "PyQt5.QtWidgets.QAction",
                                # "PyQt5.QtWidgets.qApp",
                                # "PyQt5.QtWidgets.QMenu",
                                # "PyQt5.QtWidgets.QMessageBox",
                                # "PyQt5.QtWidgets.QMainWindow",
                                # "PyQt5.QtWidgets.QApplication",
            "PyQt5.uic",
            "PyQt5.QtCore",
                                # "PyQt5.QtCore.QThread",
                                # "PyQt5.QtCore.pyqtSignal",
                                # "PyQt5.QtCore.QObject",
            "PyQt5.QtGui",
            "pynput",
            "logging",
            "sys",
            "traceback",
            "spotipy",
            "watchgod",
            "configparser",
            "os",
            "fuzzywuzzy",
            "string"]
options = {
    'build_exe': {    
        'packages':packages,
        'include_files': ["interface.ui", "icon.ico", "config.ini", "assets/"],
        'zip_include_packages':'PyQt5',
        'includes':['PyQt5.QtCore','PyQt5.QtGui', 'PyQt5.QtWidgets'],
    },    
}

setup(
    name = "SpotiLike <3",
    options = options,
    version = 1.3,
    description = 'SpotiLike🔔💕',
    executables = executables
)