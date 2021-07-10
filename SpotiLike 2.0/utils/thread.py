from PyQt5.QtCore import QThread, pyqtSignal
import sys
import os
from pynput import keyboard
import json

class GlobalHotKeys(QThread):
    signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # self.config = configparser.ConfigParser()
        
    def get_hotkeys(self) -> dict:
        with open("./config/hotkeys.json") as f:
            return json.load(f)
        

        
    def save(self, playlist:str):
        self.signal.emit(playlist)
        
    
    def hotkeys(self):
        playlists = self.get_hotkeys()
        
        keys = {}
        for playlist_name, hotkey in playlists.items():
            keys[hotkey] = lambda value="like" if playlist_name == "liked_songs" else playlist_name: self.save(value)
            
        
        return keys
        
        
    
    def run(self):
           
        while True:
            try:
                with keyboard.GlobalHotKeys(
                    self.hotkeys()
                ) as h:
                    h.join()
            except KeyError:
                pass
            
            # {"hotkey": function}