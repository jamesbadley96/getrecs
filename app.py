from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="5edd206738d347a0bc47b914ba31b4e9",
                                               client_secret="abb57184fccc40089f7dc14ccb5451b1"
                                               ))

access_token = None

@app.route("/callback", methods=['GET', 'POST'])
def callback():
    global access_token
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']                            
    return flask.redirect('/')

def get_track_id(track_name, artist_name):
    logging.info('Getting track ID for track "%s" by artist "%s"', track_name, artist_name)
    
    if access_token is None:
        logging.error("Access token not found.")
        return None

    sp = spotipy.Spotify(auth=access_token)
    results = sp.search(q=f'track:{track_name} artist:{artist_name}', type='track')
    items = results['tracks']['items']
    if not items:
        logging.warning("Can't find track: %s by artist: %s", track_name, artist_name)
        return None
    else:
        logging.info('Found track ID: %s', items[0]['id'])
        return items[0]['id']

def get_recommendations(track_id):
    logging.info('Getting recommendations for track ID: %s', track_id)
    
    if access_token is None:
        logging.error("Access token not found.")
        return None

    sp = spotipy.Spotify(auth=access_token)

    if track_id is None:
        logging.warning("Track ID is None. Can't get recommendations.")
        return None

    results = sp.recommendations(seed_tracks=[track_id])
    track_info = []
    for track in results['tracks']:
        artist_names = ', '.join([artist['name'] for artist in track['artists']])
        genres = ', '.join(sp.artist(track['artists'][0]['id'])['genres'])
        track_info.append({'name': track['name'], 'artists': artist_names, 'genres': genres})
    logging.info('Fetched recommendations successfully.')
    return track_info

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        track_name = request.form['track_name']
        artist_name = request.form['artist_name']
        track_id = get_track_id(track_name, artist_name)
        recommendations = get_recommendations(track_id)
        return render_template('results.html', track_name=track_name, artist_name=artist_name, recommendations=recommendations)
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
