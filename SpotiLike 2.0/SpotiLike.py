import json
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pynput import keyboard

import sys
from pprint import pprint as p
import spotipy
from spotipy import SpotifyOAuth
from urllib.request import urlretrieve
# import credentials Use your own credentials if you're testing.

import os
import webbrowser

from utils import thread, format_hotkey, playlists
from utils.format_hotkey import format, match, unformat

scope = "user-read-playback-state user-library-modify user-library-read playlist-read-private playlist-modify-private playlist-modify-public" # Initliaze Scopes. To read, current playing



class Home(QtWidgets.QMainWindow):
    def __init__(self):
        super(Home, self).__init__()
        uic.loadUi('uis/home.ui', self)
        self.show()
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, # Authorization.
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri="http://localhost:9000",
                                               scope=scope))
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            QIcon('icon.ico'))
        
        show_config = QAction("🗝 Show", self)
        show_assets = QAction("🌈 Assets", self)
        quit_action = QAction("❌ Exit", self)
        reload_action = QAction("🔄 Reload", self)
        reload_action.triggered.connect(self.reload)
        quit_action.triggered.connect(qApp.quit)
        show_config.triggered.connect(lambda: widget.show())
        # show_assets.triggered.connect(self.showAssets)
        tray_menu = QMenu()
        tray_menu.addAction(show_config)
        tray_menu.addAction(show_assets)
        tray_menu.addAction(reload_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    
        self.setWindowTitle("Fetching your private Playlists...")
        
        
        widget.closed.connect(self.hideMyself)
        
        self.username.setText(self.sp.me()['display_name'])
        self.logout.clicked.connect(self.log_out)
        
        # self.PLAYLISTS = self.fetch_playlists_and_songs()
        # self.setWindowTitle("SpotiLike")
        # self.selection.addItems([playlist_name for playlist_name in self.PLAYLISTS])
        # playlists.playlists_and_tracks(self.sp)
        

        # self.Thread = thread.GlobalHotKeys()
        # self.Thread.start()
        
        # self.Thread.signal.connect(self.hub)
        self.notify("SpotiLike is ready to go!")    
        
        self.selection.activated.connect(self.change_ui)
        
        self.settings.clicked.connect(lambda: widget.setCurrentWidget(window_settings))
        self.home.clicked.connect(lambda: widget.setCurrentWidget(window_home))
        self.help.clicked.connect(lambda: webbrowser.open("https://github.com/yeti2006/SpotiLike"))
        
        
        self.y = ProcessRunnable(target=None, args=self.sp)
        self.y.start()
        self.y.signal.playlists.connect(self.do_selection)
        
        liked_songs_image = QPixmap("./assets/liked_songs.ico")
        resized = liked_songs_image.scaled(self.image.width(), self.image.height())
        self.image.setPixmap(resized)
          
        self.shortcut.textChanged.connect(self.change_shortcut)
        
        
        
    @pyqtSlot(str)
    def save(self, value):
        if type == "liked":
            print("Saved songs.")
            self.like()
            
        else:
            for key, v in self.playlists.items():
                if self.playlists[key]['name'] == value:
                    value= key
                    break 
            
            with open("./config/settings.json") as f:
                self.settings_data= json.load(f)
            if self.settings_data['auto_like'] is True:
                self.liked(playlist=True)
            self.playlists(value)
            print(value)
       
    def like(self, playlist:bool=False):
        current = self.sp.current_playback()
        if not current:
            return self.notify('Not playing anything')
        try:
            self.sp.current_user_saved_tracks_add(tracks=[current['item']['id']])
            if not playlist:
                self.notify(f"❤ Saved [{current['item']['name']}] by {current['item']['album']['artists'][0]['name']} to Liked Songs.",
                            "like")
        except Exception as e:
            self.notify(f"An unexpected error occured. Error: {e}. | Please Try Again?", "error")
         
            
    def playlist(self, name):
        
        current = self.sp.current_playback()
        if not current:
            return self.notify("Not playing anything")
        
        with open("./config/data.json") as f:
            self.songs=json.load(f)
        
        if current['item']['id'] in self.songs[name]:
            return self.notify(f"[{current['item']['name']}] by {current['item']['album']['artists'][0]['name']} is saved in {name} already.",
                               name)
        try:
            playlist = name

            self.songs[name].append(current['item']['id'])
            
            self.sp.playlist_add_items(self.PLAYLISTS[name]['playlist_id'], items=[current['item']['id']])
            self.notify(f"❤ Saved [{current['item']['name']}] by {current['item']['album']['artists'][0]['name']} to [{playlist}] playlist.",
                        name)
        except Exception as e:
            self.notify(f"An unexpected error occured. Error: {e}. ", "error")
    
    @pyqtSlot(dict)
    def do_selection(self, value):
        self.playlists = value
        
        keys = self.change_shortcut()
        self.shortcut.setText(keys['liked_songs'])
        
        self.selection.addItems([value[x]['name'] for x in value])
        
        with open("./config/data.json") as f:
            data=json.load(f)
            
        data = value
        with open("./config/data.json", "w") as f:
            json.dump(data, f, indent=4)
            
        self.start_thread()
        
    def reload(self):
        self.tray_icon.showMessage(
            "SpotiLike",
            "Reloaded SpotiLike.",
            QIcon('./SpotiLike/icon.ico'),
            2000
        )
        python = sys.executable
        os.execl(python, python, * sys.argv)
        
        
    def hideMyself(self):
        self.tray_icon.showMessage(
                "SpotiLike",
                "Application was minimized to Tray",
                QIcon('icon.ico'),
                2000
            )
        
    def notify(self, msg, icon=None):
        icon = f"./assets/liked_songs.ico" if icon=="like" else f"./assets/playlists/{icon}.ico"
        self.tray_icon.showMessage(
                "SpotiLike",
                msg,
                QIcon(icon),
                2000
            )
    
    def change_ui(self):
        current_text = self.selection.currentText()
        
        with open("./config/hotkeys.json") as f:
            data = json.load(f)
        
        self.shortcut.setText(unformat(data["liked_songs"] if current_text == "Saved Songs" else data[current_text]))
        
        if current_text == "Saved Songs":
            image = QPixmap("./assets/liked_songs.ico")
            resized = image.scaled(self.image.width(), self.image.height())
            self.image.setPixmap(resized)
            return 

        for key in self.playlists:
             if self.playlists[key]['name'] == current_text:
                 image = QPixmap(self.playlists[key]['image_url'])
                 resized = image.scaled(self.image.width(), self.image.height())
                 self.image.setPixmap(resized)
                 
    def change_shortcut(self):
        with open("./config/hotkeys.json") as f:
            data = json.load(f)
        
        if data == {}:
            data["liked_songs"] = "<ctrl>+<shift>+l"
            self.shortcut.setText(unformat(data["liked_songs"] if self.selection.currentText() == "Saved Songs" else self.selection.currentText()))
            count = 0
            for playlist_id in self.playlists:
                count+=1
                data[self.playlists[playlist_id]['name']] = format(match(f"alt+{count}"))
                
                
        else:
            data["liked_songs" if self.selection.currentText() == "Saved Songs" else self.selection.currentText()] = format(match(self.shortcut.text()))
    
        with open("./config/hotkeys.json", "w") as f:
            json.dump(data, f, indent=4)
            
        return data
        
        
            
    def log_out(self):
        self.notify("Logged out from Spotify as {}".format(self.sp.me()['display_name']))
        os.remove("./.cache")
        self.reload()
        
    def start_thread(self):
        self.hotkeyz = thread.GlobalHotKeys()
        self.hotkeyz.start()
        self.hotkeyz.signal.connect(self.save)
        
    # def start_new_thread(self):
    #     self.hotkeyz.exit()
    #     self.hotkeyz.start()
    #     self.hotkeyz.signal.connect(self.save)
    
class WorkerSignals(QObject):
    playlists = pyqtSignal(dict)        
    
class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args
        self.signal = WorkerSignals()

    def run(self):
        print("started")
        data = playlists.main(self.args)
        self.signal.playlists.emit(data)
        print("done")

    def start(self):
        QThreadPool.globalInstance().start(self)

        
if __name__ == "__main__":
    from interfaces import main, settings
    
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('/icon.ico'))
    
    widget = main.MainWidget()
    
    window_home = Home()
    window_settings = settings.Settings(widget)
    
    widget.addWidget(window_home)
    widget.addWidget(window_settings)
    
    widget.setFixedSize(window_home.width(), window_home.height())
 
    
    widget.show()
    
    app.exec_()
    
