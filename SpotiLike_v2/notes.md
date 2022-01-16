Use widget class to do it.

playlist dict:
    
```py
def fetch_playlists_and_songs(self):
        private_playlists = dict((x['name'], {"playlist_id": x['id'], "tracks": [], "images": x['images'][0]['url']}) for x in self.sp.current_user_playlists()['items'] if x['owner']['id'] == self.sp.me()['id'])
        
        for playlist in private_playlists:
            try:
                results = self.sp.playlist_tracks(private_playlists[playlist]['playlist_id'])
            except Exception as e:
                print(e)
                self.notify(f"An unexpected error occured. {e}", "error")
                return
            
            songs = [song['track']['id'] for song in results['items']]
            
            private_playlists[playlist]["tracks"] = songs
            
        return private_playlists
```

```py
[{current['item']['name']}] by {current['item']['album']['artists'][0]['name']}
```