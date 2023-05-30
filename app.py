from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="5ef3272dcd5e49598a655deb26b81aeb",
                                               client_secret="f6b712b3f7c1407396dc3cc2ed9f0e5f",
                                               redirect_uri="http://localhost:8080"
                                               ))

app = Flask(__name__)

def get_track_id(track_name, artist_name):
    """Search for a track by name and artist, and return its Spotify ID."""
    results = sp.search(q=f'track:{track_name} artist:{artist_name}', type='track')
    items = results['tracks']['items']
    if not items:
        print("Can't find track:", track_name, "by artist:", artist_name)
        return None
    else:
        return items[0]['id']  # return the id of the first match

def get_recommendations(track_id):
    """Get recommendations based on a track ID."""
    if track_id is None:
        print("Track ID is None. Can't get recommendations.")
        return None
    results = sp.recommendations(seed_tracks=[track_id])
    track_info = []
    for track in results['tracks']:
        artist_names = ', '.join([artist['name'] for artist in track['artists']])
        genres = ', '.join(sp.artist(track['artists'][0]['id'])['genres'])
        track_info.append({'name': track['name'], 'artists': artist_names, 'genres': genres})
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
