from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QSystemTrayIcon, QAction, qApp, QMenu, QMessageBox
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QIcon

from pynput import keyboard

import sys
import traceback
import logging

import spotipy
from spotipy import SpotifyOAuth
import configparser
from watchgod import watch, Change

# import credentials Use your own credentials if you're testing.

import os

from fuzzywuzzy import process
from string import ascii_lowercase as english

log = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(handler)

scope = "user-read-playback-state user-library-modify user-library-read playlist-read-private playlist-modify-private playlist-modify-public" # Initliaze Scopes. To read, current playing


HOTKEY_PREFIXES = [
    'ctrl',
    'alt',
    'shift',
    'esc'
]

def format(key:str):
    key.lower()
    if key.endswith("+"):
        key[:-1]
        

    result = [i for i in [f"<{thing}>" if any(map(key.__contains__, HOTKEY_PREFIXES)) and thing in HOTKEY_PREFIXES else thing for thing in key.split('+')] if i]
            
    return "+".join(result) 

def match(keys:str):
    
    result = list(dict.fromkeys([process.extractOne(key, HOTKEY_PREFIXES)[0] for key in keys.split('+') if not key in english and not key in [str(no) for no in range(10)]] + [keys for keys in keys.split('+') if  keys in english or keys in [str(x) for x in range(10)]]))

    return "+".join(result)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('./interface.ui', self)
        self.show()
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, # Authorization.
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri="http://localhost:9000",
                                               scope=scope))
        self.sp.me()
        print("ok")
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            QIcon('./icon.ico'))
        
        show_config = QAction("🗝 Config", self)
        show_assets = QAction("🌈 Icons", self)
        quit_action = QAction("❌ Exit", self)
        reload_action = QAction("🔄 Reload", self)
        logout_action = QAction("☠ Logout", self)
        reload_action.triggered.connect(self.reload)
        quit_action.triggered.connect(qApp.quit)
        show_config.triggered.connect(self.showConfig)
        show_assets.triggered.connect(self.showAssets)
        logout_action.triggered.connect(self.notify)
        tray_menu = QMenu()
        tray_menu.addAction(show_config)
        tray_menu.addAction(show_assets)
        tray_menu.addAction(reload_action)
        tray_menu.addAction(quit_action)
        tray_menu.addAction(logout_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.hideMyself()
        
        
        # self.runnable = GetPLaylists(self, (self.sp, self.read_config()))
        # self.runnable.start()
        self.notify("Fetching tracks...")
        self.playlistx = self.getTracks(self.read_config())
        self.playlist_tracks(self.playlistx)
        # self.runnable.signal.playlists.connect(self.playlist_tracks)
        
        self.watch = WatchConfig()
        self.watch.start()
        self.watch.edited.connect(self.reload_config)
          
    def reload_config(self):
        self.notify("Changes detected to config file! Reloading...")
        self.reload()
          
    def logout(self):
        os.remove(".cache")
        self.reload()
        
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "SpotiLike",
            "Application was minimized to Tray",
            QIcon('icon.ico'),
            2000
        )
            
    def reload(self):
        self.tray_icon.showMessage(
            "SpotiLike",
            "Reloaded SpotiLike.",
            QIcon('./icon.ico'),
            2000
        )
        python = sys.executable
        os.execl(python, python, * sys.argv)
        
    def showConfig(self):
        os.startfile(os.getcwd()+"/config.ini")
        
    def showAssets(self):
        os.startfile(os.getcwd()+"/assets/")
        
    def hideMyself(self):
        self.hide()
        self.tray_icon.showMessage(
                "SpotiLike",
                "Application was minimized to Tray",
                QIcon('icon.ico'),
                500
            )
        
    def notify(self, msg, icon="default"):
        icon = f"./assets/{icon}.ico"
        self.tray_icon.showMessage(
                "SpotiLike",
                msg,
                QIcon(icon),
                2000
            )
 
    # @pyqtSlot(dict)
    def playlist_tracks(self, value):
        log.info("Recieved tracks")
        self.notify("SpotiLike is ready to go!")
        self.songs = value
        self.Thread = MainThread({name: key['key'] for name,key in self.read_config().items()}, self.like_key())
        self.Thread.start()  
        self.Thread.signal.connect(self.hub)
 
    @pyqtSlot(str)
    def hub(self, value):
        print(value)
        if value == "yetilikesstrawberriesbecausestrawberriesarecool": 
            self.like()
        else:
            if self.settings() is True:
                self.like(playlist=True)
            self.playlist(value)
            
    def like(self, playlist:bool=False):
        current = self.sp.current_playback()
        if not current or current['item'] is None:
           self.notify('Not playing anything')
           return
        try:
            self.sp.current_user_saved_tracks_add(tracks=[current['item']['id']])
            if not playlist:
                self.notify(f"❤ Saved [{current['item']['name']}] by {current['item']['album']['artists'][0]['name']} to Liked Songs.",
                            "heart")
        except Exception as e:
            self.notify(f"An unexpected error occured. Error: {e}. Try Again?", "error")
            
    def playlist(self, name):
        
        current = self.sp.current_playback()
        if not current or current['item'] is None:
            self.notify("Not playing anything")
            return
        
        if current['item']['id'] in self.songs[name]:
            return self.notify(f"[{current['item']['name']}] by {current['item']['album']['artists'][0]['name']} is saved in [{name}] already.",
                               name)
        try:
            playlist = name

            self.songs[name].append(current['item']['id'])
            
            self.sp.playlist_add_items(self.PLAYLISTS[name]['playlist'], items=[current['item']['id']])
            self.notify(f"❤ Saved [{current['item']['name']}] by {current['item']['album']['artists'][0]['name']} to [{playlist}] playlist.",
                        name)
        except Exception as e:
            self.notify(f"An unexpected error occured. Error: {e}. Try Again?", "error")
            
    
    def read_config(self):
        config = configparser.ConfigParser()
        config.read("./config.ini")
            
        filtered = [x for x in config if not x.startswith("DEFAULT") and not x.startswith("Liked Songs")]

        PLAYLISTS = {}
        for playlist in filtered:
            PLAYLISTS[playlist] = {}
            for k,v in config[playlist].items():
                new = {k:v}
                PLAYLISTS[playlist].update(new)
        try:
            for k,v in PLAYLISTS.items():
                v['key'] = format(match(v['key']))
                v['playlist'] = v['playlist'] if len(v['playlist']) == 22 else v['playlist'].split("/")[4] 
        except KeyError:
            return {}  

        self.PLAYLISTS = PLAYLISTS
        return PLAYLISTS
    
    def like_key(self):
        config = configparser.ConfigParser()
        config.read("./config.ini")
        
        return {"yetilikesstrawberriesbecausestrawberriesarecool": format(match(config['Liked Songs']['key']))}
        
    def settings(self):
        config = configparser.ConfigParser()
        config.read("./config.ini")
        
        if config['Liked Songs']['auto_like_for_playlist'].lower() == "yes":
            return True 
        return False
    
    def getTracks(self, playlists):
        self.playlists = playlists
        data = {}
        for playlist in self.playlists:
            
            results = self.sp.playlist_tracks(self.playlists[playlist]['playlist'])
            
            tracks = results['items']
        
            data[playlist] = ""
        
            songx = []
            for y in tracks:
                songs =  y['track']['id']
                songx.append(songs)
                
            data.update({playlist: songx})

        return data
            
class MainThread(QThread):
    signal = pyqtSignal(str)
    
    def __init__(self, hotkeys, like):
        super().__init__()
        self.hotkeys = hotkeys
        self.like = like
        self.hotkeys.update(self.like)
             
    def save(self, playlist:str):
        self.signal.emit(playlist)
        
    def assign_funcs_to_hotkeys(self):
        hotkeys = {}
        print(self.hotkeys)
        for key, value in self.hotkeys.items():
            hotkeys[value] = lambda playlist_name=key: self.save(playlist=playlist_name)
        
        print(hotkeys)
        return hotkeys

    def run(self): 
        while 1:
            with keyboard.GlobalHotKeys(
                self.assign_funcs_to_hotkeys()
            ) as h:
                h.join()
            
                
class WatchConfig(QThread):
    edited = pyqtSignal()
    def __init__(self):
        super().__init__()
        
    def run(self):
        for changes in watch('./config.ini'):
            for i in changes:
                if i[0] == Change.modified:
                    self.edited.emit()

"""I had to avoid using QRunnable beacuse the exe compilers I tried doesn't seem to work
    with a QRunnable instance. I had to put it inside my main window class which will still
    cause the gui to freeze. I should probably find a way around this."""

# class WorkerSignals(QObject):
#     playlists = pyqtSignal(dict)        
# class GetPLaylists(QRunnable):
#     def __init__(self, target, args):
#         QRunnable.__init__(self)
#         self.t = target
#         self.args = args
#         self.sp = self.args[0]
#         self.playlists = self.args[1]
#         self.signal = WorkerSignals()
      
    
#     def getTracks(self):
#         data = {}
#         for playlist in self.playlists:
            
#             results = self.sp.playlist_tracks(self.playlists[playlist]['playlist'])
            
#             tracks = results['items']
        
#             data[playlist] = ""
        
#             songx = []
#             for y in tracks:
#                 songs =  y['track']['id']
#                 songx.append(songs)
                
#             data.update({playlist: songx})

#         return data

#     def run(self):
#         print("started")
        
#         tracks = self.getTracks()
      
#         self.signal.playlists.emit(tracks)
#         print("done")

    

#     def start(self):

#         QThreadPool.globalInstance().start(self)
        

def show_exception_box(log_msg):

    if QtWidgets.QApplication.instance() is not None:
            errorbox = QtWidgets.QMessageBox()
            errorbox.setIcon(QMessageBox.Critical)
            errorbox.setText("Oops. Something unexpected happened in SpotiLike:\n{0}\n\nClicking Ok to restart!".format(log_msg))
            errorbox.setStandardButtons(QMessageBox.Ok)
            errorbox.buttonClicked.connect(lambda: os.execl(sys.executable, sys.executable, *sys.argv))
            errorbox.exec_()
    else:
        log.debug("No QApplication instance available.")

 
class UncaughtHook(QObject):
    _exception_caught = pyqtSignal(object)
 
    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        sys.excepthook = self.exception_hook

        self._exception_caught.connect(show_exception_box)
 
    def exception_hook(self, exc_type, exc_value, exc_traceback):
        
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            exc_info = (exc_type, exc_value, exc_traceback)
            log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                 '{0}: {1}'.format(exc_type.__name__, exc_value)])
            log.critical("Uncaught exception:\n {0}".format(log_msg), exc_info=exc_info)

 
            self._exception_caught.emit(log_msg)

qt_exception_hook = UncaughtHook()
        
if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('./icon.ico'))
    window = Ui()
    app.exec_()
    
