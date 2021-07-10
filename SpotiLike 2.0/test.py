from pynput import keyboard

with keyboard.GlobalHotKeys(
    {"<ctrl>+l": lambda: print("yes")}) as w:
        w.join()
    