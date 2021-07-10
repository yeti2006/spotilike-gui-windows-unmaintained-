from PyQt5 import QtWidgets
from PyQt5 import uic

import json
import webbrowser

settings = [
    "fetch_playlists", 
    "fetch_songs",
    "show_notif",
    "auto_like"
]

class Settings(QtWidgets.QMainWindow):
    def __init__(self, widget):
        super(Settings, self).__init__()
        uic.loadUi("./uis/settings.ui", self)
        self.show()
        self.widget = widget
        
        self.setupSettings()
        self.home.clicked.connect(lambda: self.widget.setCurrentIndex(widget.currentIndex()-1))
        self.help.clicked.connect(lambda: webbrowser.open("https://github.com/yeti2006/SpotiLike"))
        
        for x in settings:
            getattr(self, x).stateChanged.connect(lambda item=x: self.change_setting(item))
        
    def setupSettings(self):
        with open("config/settings.json") as f:
            data=json.load(f)
            
        if data == {}:
            
            for item in settings:
                do = getattr(self, item)
                do.setChecked(True)
                data[item] = True 
                
            with open("config/settings.json", 'w') as f:
                json.dump(data, f, indent=4)
        else:
            for x in data:
                do = getattr(self, x)
                do.setChecked(data[x])

    def change_setting(self, item):
        with open("config/settings.json") as f:
            data=json.load(f)
         
        
        for item in settings:
            do = getattr(self, item)
            data[item] = True if do.isChecked() else False
            
        with open("config/settings.json", 'w') as f:
            json.dump(data, f, indent=4)
            
        