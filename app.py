from flask import Flask, render_template, request, session
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
Session(app)

sp_oauth = SpotifyOAuth(client_id="5ef3272dcd5e49598a655deb26b81aeb",
                        client_secret="f6b712b3f7c1407396dc3cc2ed9f0e5f",
                        redirect_uri="http://localhost:8080/callback"
                        )

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'sp' not in session:
        auth_url = sp_oauth.get_authorize_url()
        return flask.redirect(auth_url)
    # rest of your code...

@app.route("/callback", methods=['GET', 'POST'])
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']                            

    # Create Spotify client with this token
    sp = spotipy.Spotify(auth=access_token)

    # Save the Spotify client to the session
    session['sp'] = sp

    return flask.redirect('/')  # redirect back to the main page


def get_track_id(track_name, artist_name):
    logging.info('Getting track ID for track "%s" by artist "%s"', track_name, artist_name)

    # Retrieve the access_token from the session
    access_token = session.get('access_token', None)

    if access_token is None:
        logging.error("Access token not found in session.")
        return None

    # Create a new Spotify client with the access token
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

    # Retrieve the access_token from the session
    access_token = session.get('access_token', None)

    if access_token is None:
        logging.error("Access token not found in session.")
        return None

    # Create a new Spotify client with the access token
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
