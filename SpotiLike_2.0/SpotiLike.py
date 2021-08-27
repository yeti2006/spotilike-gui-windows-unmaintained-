import json
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pynput import keyboard

import sys
import logging
from pprint import pprint as p
import spotipy
from spotipy import SpotifyOAuth
from urllib.request import urlretrieve
import logging

import os
import webbrowser
# import credentials Use your own credentials if you're testing.

sys.path.append(os.path.abspath('./utils/'))
sys.path.append(os.path.abspath('./interfaces/'))

import error_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("spotilike_logs.log"),
        logging.StreamHandler()
    ]
)

import thread, playlists
from format_hotkey import *


scope = "user-read-playback-state user-library-modify user-library-read playlist-read-private playlist-modify-private playlist-modify-public" # Initliaze Scopes. To read, current playing



class Home(QtWidgets.QMainWindow):
    def __init__(self):
        super(Home, self).__init__()
        uic.loadUi('uis/home.ui', self)
        self.show()
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, # Authorization.
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri="http://localhost:9000",
                                               scope=scope))
        except Exception as e:
            print(e)
            self.reload()
            
        logging.info("Authorised and verified credentials from localhost:9000")
        
        self.sp.me()
        logging.info("API called to verify user is authenticated.")
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            QIcon('icon.ico'))
        
        show = QAction("🗝 Show", self)
        show_assets = QAction("🌈 Assets", self)
        quit_action = QAction("❌ Exit", self)
        reload_action = QAction("🔄 Reload", self)
        reload_action.triggered.connect(self.reload)
        quit_action.triggered.connect(qApp.quit)
        show.triggered.connect(lambda: widget.show())
        # show_assets.triggered.connect(self.showAssets)
        tray_menu = QMenu()
        tray_menu.addAction(show)
        tray_menu.addAction(show_assets)
        tray_menu.addAction(reload_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    
        self.setWindowTitle("Fetching your private Playlists...")
        
        widget.closed.connect(self.hideMyself)
        
        self.username.setText(self.sp.me()['display_name'])
        self.logout.clicked.connect(self.log_out)
         
                 
        self.selection.activated.connect(self.change_ui)
        
        self.settings.clicked.connect(lambda: widget.setCurrentWidget(window_settings))
        self.home.clicked.connect(lambda: widget.setCurrentWidget(window_home))
        self.help.clicked.connect(lambda: webbrowser.open("https://github.com/yeti2006/SpotiLike"))
        self.applyChanges.clicked.connect(self.reloadHotkeys)
        self.applyChanges.setEnabled(False)
        self.isHotkeyzRunning = False
        
        
        self.playlistThread = ProcessRunnable(target=None, args=self.sp)
        self.playlistThread.start()
        logging.info("Playlist thread started")
        widget.setWindowTitle("SpotiLike | Downloading assets and playlist data...")
        self.playlistThread.signal.playlists.connect(self.do_selection)
        
        liked_songs_image = QPixmap("./assets/liked_songs.ico")
        resized = liked_songs_image.scaled(self.image.width(), self.image.height())
        self.image.setPixmap(resized)
          
        self.shortcut.textChanged.connect(self.change_shortcut)
        
        self.changesSaved = False
        
    
        
    @pyqtSlot(str)
    def save(self, value):
        print(value)
        if value == "like":
            print("Saved songs.")
            self.like()
            
        else:
            for key, v in self.playlists.items():
                if key == value:
                    value = key
                    break 
            
            with open("./config/settings.json") as f:
                self.settings_data= json.load(f)
            if self.settings_data['auto_like'] is True:
                self.like(playlist=True)
                
            self.playlist(value, self.settings_data['fetch_songs'])

       
    def like(self, playlist:bool=False):
        current = self.sp.current_playback()
        if not current or current['item'] is None:
            return self.notify('Not playing anything', "error")
        try:
            self.sp.current_user_saved_tracks_add(tracks=[current['item']['id']])
            
            urlretrieve(current['item']['album']['images'][0]['url'], "./assets/song.ico")
            
            if not playlist:
                self.notify(f"❤ Saved [{current['item']['name']}] by {current['item']['album']['artists'][0]['name']} to Liked Songs.")
        except Exception as e:
            self.notify(f"An unexpected error occured. Error: {e}. | Please Try Again?", "error")
            
         
            
    def playlist(self, name, tracks):
        
        current = self.sp.current_playback()
        if not current or current['item'] is None:
            return self.notify("Not playing anything")
        
        with open("./config/data.json") as f:
            self.songs=json.load(f)
            
        if tracks:
            if current['item']['id'] in self.songs[name]['tracks']:
                return self.notify(f"[{current['item']['name']}] by {current['item']['album']['artists'][0]['name']} is saved in {name} already.", "error")
        try:
            playlist = name

            
            self.sp.playlist_add_items(self.playlists[name]['id'], items=[current['item']['id']])
            if tracks: self.songs[name]['tracks'].append(current['item']['id'])
            
            urlretrieve(current['item']['album']['images'][0]['url'], "./assets/song.ico")

            self.notify(f"❤ Saved [{current['item']['name']}] by {current['item']['album']['artists'][0]['name']} to [{playlist}] playlist.")
        except Exception as e:
            self.notify(f"An unexpected error occured. Error: {e}. ", "error")
    
    @pyqtSlot(dict)
    def do_selection(self, value):
        logging.info("Playlists and/or tracks downloaded.")
        widget.setWindowTitle("SpotiLike <3")
        
        self.playlists = value
        
        with open("./config/hotkeys.json") as f:
            data = json.load(f)
        
        if data == {}:
            data["liked_songs"] = "<ctrl>+l"
            self.shortcut.setText(unformat(data["liked_songs"] if self.selection.currentText() == "Saved Songs" else self.selection.currentText()))
            for name in self.playlists:
                data[name] = None
                
            
        else:
            for name in self.playlists:
                if not name in data or data[name] == "":
                    data[name] = None
           
        with open("./config/hotkeys.json", "w") as f:
            json.dump(data, f, indent=4)
            
        self.shortcut.setText(unformat(data['liked_songs']))
        
        self.selection.addItems([x for x in value])
        
        with open("./config/data.json") as f:
            data=json.load(f)
            
        data = value
        with open("./config/data.json", "w") as f:
            json.dump(data, f, indent=4)
            
        self.start_thread()
        
    def reload(self):
        logging.info("Restarting ")
        python = sys.executable
        os.execl(python, python, * sys.argv)
        
        
    def hideMyself(self):
        logging.info("Hiding widget.")
        
        if self.changesSaved == False:
            logging.debug("Changes are not saved.")
            self.reloadHotkeys()
        
        self.tray_icon.showMessage(
                "SpotiLike",
                "Application was minimized to Tray",
                QIcon('icon.ico'),
                2000
            )
        
    def notify(self, msg, icon="./assets/song.ico"):
        # icon = f"./assets/liked_songs.ico" if icon=="like" else f"./assets/playlists/{icon}.ico"
        if icon == "error" or icon == "liked_songs":
            icon = "./assets/{}.ico".format(icon)
            
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

        for key, value in self.playlists.items():
             if key == current_text:
                 logging.debug(f"Changed pixmap: {current_text} to ID -> {value['id']}")
                 image = QPixmap(value['image_url'])
                 resized = image.scaled(self.image.width(), self.image.height())
                 self.image.setPixmap(resized)
                 
    def change_shortcut(self):
        self.changesSaved = False
        
        with open("./config/hotkeys.json") as f:
            data = json.load(f)
        if data == {}:
            data["liked_songs"] = "<ctrl>+l"
            self.shortcut.setText(unformat(data["liked_songs"] if self.selection.currentText() == "Saved Songs" else self.selection.currentText()))
            count = 0
            for name in self.playlists:
                if not name == "liked_songs":
                    data[name] = None
                
            
        else:
            for name in self.playlists:
                if not name in data or data[name] == "":
                    data[name] = "<alt>+?"
            if self.shortcut.text().lower() == "none" or not self.shortcut.text().lower():
                data["liked_songs" if self.selection.currentText() == "Saved Songs" else self.selection.currentText()] = None
            else:
                data["liked_songs" if self.selection.currentText() == "Saved Songs" else self.selection.currentText()] = format(match(self.shortcut.text()))
    
       
        with open("./config/hotkeys.json", "w") as f:
            json.dump(data, f, indent=4)
           

        return data
        
        
            
    def log_out(self):
        self.notify("Logged out from Spotify as {}".format(self.sp.me()['display_name']), "liked_songs")
        os.remove("./.cache")
        self.reload()
        
    def start_thread(self):
        logging.info("Hotkey thread started.")
        
        self.hotkeyz = thread.GlobalHotKeys()
        self.hotkeyz.start()
        self.hotkeyz.signal.connect(self.save)
        self.isHotkeyzRunning = True
        self.applyChanges.setEnabled(True)
        
    def reloadHotkeys(self):
        self.hotkeyz.restart()
        logging.info("Restarted hotkeyz")
        self.changesSaved = True
        
        
    
class WorkerSignals(QObject):
    playlists = pyqtSignal(dict)        
    
class ProcessRunnable(QThread):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args
        self.signal = WorkerSignals()

    def run(self):
        data = playlists.main(self.args)
        self.signal.playlists.emit(data)
        logging.info("Playlists obtained")


        
if __name__ == "__main__":
     
    import main, settings
    
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('./icon.ico'))
    
    widget = main.MainWidget()
    
    window_home = Home()
    window_settings = settings.Settings(widget)
    
    widget.addWidget(window_home)
    widget.addWidget(window_settings)
    
    widget.setFixedSize(window_home.width(), window_home.height())
 
    
    widget.show()
    
    app.exec_()
    
