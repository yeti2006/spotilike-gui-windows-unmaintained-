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

    def get_hotkeys(self) -> dict:
        """Returns hotkey data"""

        with open("./config/hotkeys.json") as f:
            return json.load(f)

    def save(self, playlist: str):
        """Method that emits the signal to activate the hotkey"""
        self.signal.emit(playlist)

    def hotkeys(self):
        """Returns a dict with lambda functions for each hotkey like:
        {
            "hotkey" : lambda value: self.save(value),
            ...
        }"""

        playlists = self.get_hotkeys()
        playlists = {x: y for x, y in playlists.items() if y}
        keys = {}
        for playlist_name, hotkey in playlists.items():
            keys[
                hotkey
            ] = lambda value="like" if playlist_name == "liked_songs" else playlist_name: self.save(
                value
            )

        return keys

    def restart(self):
        """Restarts the hotkey loop"""

        logging.warn("Stopping hotkey loop.")
        self.x.stop()
        logging.info("Starting hotkey loop.")

        self._run()

    def run(self):
        """QThread convenience method to start the thread"""

        self._run()

    def _run(self):
        """Actually starts the hotkey loop and registers them."""

        self.x = keyboard.GlobalHotKeys(self.hotkeys())

        self.x.start()
