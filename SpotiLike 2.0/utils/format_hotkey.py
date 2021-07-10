from fuzzywuzzy import process
from string import ascii_lowercase as english
from collections import Counter

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

def unformat(keys:str):
    result = [i for i in [key.strip("<>") for key in keys.split('+')]]
    
    return "+".join(result)
    
print(format(match("ctrl+l+shift+2+ctrl+shift+alt")))