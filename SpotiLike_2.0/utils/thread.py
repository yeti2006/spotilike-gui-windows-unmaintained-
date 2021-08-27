from PyQt5.QtCore import QThread, pyqtSignal
import sys
import os
from pynput import keyboard
import json
import logging

logging.getLogger(__name__)

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
        playlists = {x: y for x,y in playlists.items() if y}
        keys = {}
        for playlist_name, hotkey in playlists.items():
            keys[hotkey] = lambda value="like" if playlist_name == "liked_songs" else playlist_name: self.save(value)
            
        
        return keys
        
    def restart(self):
        logging.warn("Stopping hotkey loop.")
        self.x.stop()
        logging.info("Starting hotkey loop.")
        # self.x = keyboard.GlobalHotKeys(
        #     self.hotkeys()
        # )

        # self.x.start()
        self._run()

    
    def run(self):
           
        # while True:
        
            
        self.x = keyboard.GlobalHotKeys(
            self.hotkeys()
        )

        self.x.start()
        
    def _run(self):
           
        # while True:
        
            
        self.x = keyboard.GlobalHotKeys(
            self.hotkeys()
        )

        self.x.start()

            
        
            
            # {"hotkey": function}
      
