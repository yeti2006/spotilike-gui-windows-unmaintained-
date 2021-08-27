import os
from pprint import pprint as p
from urllib.request import urlretrieve
import json
import logging; logging.getLogger(__name__)

def playlists_and_tracks(spotify) -> dict:
    
    playlists_and_tracks = {}
    
    for item in spotify.current_user_playlists()['items']:
        if item['owner']['id'] == spotify.me()['id']:
            playlists_and_tracks[item['name']] = {
                "id": item['id'],
                "image_url": item['images'][0]['url'] if not item['images'] == [] else "./assets/error.ico", 
                "tracks": [song['track']['id'] for song in spotify.playlist_tracks(item['id'])['items']]
            }
    
    return playlists_and_tracks

def get_playlists(spotify) -> dict:
    playlists = {
        str(item['name']): {
            "id":item['id'],
            "image_url": item['images'][0]['url'] if not item['images'] == [] else "./assets/error.ico"
            }
        for item in spotify.current_user_playlists()['items'] if item['owner']['id'] == spotify.me()['id']
        }
    
    return playlists
    
def save_images(playlists) -> None:
    images = {y['id']: y['image_url'] for x,y in playlists.items()}

    for id, url in images.items():
        if not os.path.exists(f"./assets/playlists/{id}.ico"):
            try:
                urlretrieve(url, f"./assets/playlists/{id}.ico")
            except: pass
            
            print(f"Saved {id}.ico")
    logging.info("Playlist icons downloaded")
            
def settings() -> dict:
    with open("./config/settings.json") as f:
        data = json.load(f)
    return data
            
def main(spotify):
    if settings()['fetch_playlists'] and settings()['fetch_songs']:
        data = playlists_and_tracks(spotify)
        
    elif settings()['fetch_playlists']:
        data = get_playlists(spotify)
    
    else:
        with open("./config/data.json") as f:
            data=json.load(f)
    save_images(data)
    for x in data:
        data[x]['image_url'] = f"./assets/playlists/{data[x]['id']}.ico"
        

    return data