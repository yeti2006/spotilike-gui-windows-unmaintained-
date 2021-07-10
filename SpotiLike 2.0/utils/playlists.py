import os
from pprint import pprint as p
from urllib.request import urlretrieve
import json

def playlists_and_tracks(spotify) -> dict:
    
    playlists_and_tracks = {}
    
    for item in spotify.current_user_playlists()['items']:
        if item['owner']['id'] == spotify.me()['id']:
            playlists_and_tracks[item['id']] = {
                "name": item['name'],
                "image_url": item['images'][0]['url'], 
                "tracks": [song['track']['id'] for song in spotify.playlist_tracks(item['id'])['items']]
            }
    
    return playlists_and_tracks

def get_playlists(spotify) -> dict:
    print("called get_playlists")
    playlists = {
        str(item['id']): {
            "name":item['name'],
            "image_url": item['images'][0]['url'] 
            }
        for item in spotify.current_user_playlists()['items'] if item['owner']['id'] == spotify.me()['id']
        }
    
    return playlists
    
def save_images(playlists) -> None:
    print("Called save_images")
    images = {x: playlists[x]['image_url'] for x in playlists}
    
    if os.listdir("./assets/playlists/") == []:
        for playlist, url in images.items():
            urlretrieve(url, f"./assets/playlists/{playlist}.ico")
            
            
def settings():
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
        data[x]['image_url'] = f"./assets/playlists/{x}.ico"
        
    print(p(data))
    return data