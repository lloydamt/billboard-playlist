import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from decouple import config
from datetime import datetime

scope = "user-library-read playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config('SPOTIPY_CLIENT_ID'),
                                               client_secret=config('SPOTIPY_CLIENT_SECRET'),
                                               redirect_uri=config('SPOTIPY_REDIRECT_URI'),
                                               scope=scope))

my_id = sp.me()['id']
today = f"{datetime.now().date().strftime('%d-%m-%Y')}"

URL = "https://www.billboard.com/charts/hot-100/"
response = requests.get(URL)
billboard_webpage = response.text

soup = BeautifulSoup(billboard_webpage, "html.parser")

titles = soup.select("li h3#title-of-a-story")
songs = [title.getText().strip() for title in titles]
artist_tags = soup.select("li.o-chart-results-list__item span.a-no-trucate")
artists = [artist.text.strip().split()[0] for artist in artist_tags]

song_uris = []
for index, song in enumerate(songs):
    try:
        song_title = sp.search(q=f"{song} {artists[index]}", limit=1, type='track')
        uri = song_title['tracks']['items'][0]['uri']
    except IndexError:
        continue
    else:
        song_uris.append(uri)

new_playlist = sp.user_playlist_create(user=my_id, name=f"Billboard Hot-100 {today}", public=True)

sp.playlist_add_items(playlist_id=new_playlist['id'], items=song_uris)
print('Playlist created')