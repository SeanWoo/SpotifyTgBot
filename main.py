SPOTIPY_CLIENT_ID = None
SPOTIPY_CLIENT_SECRET = None
SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080/api/callback'
SPOTIPY_SCOPE = "user-read-playback-state,user-modify-playback-state"

import json
import os
from flask import Flask, session, request, redirect, jsonify
from flask_session import Session
import spotipy
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

with open("config.json", "r") as f:
    obj = json.loads(f.read())
    SPOTIPY_CLIENT_ID = obj["SPOTIPY_CLIENT_ID"]
    SPOTIPY_CLIENT_SECRET = obj["SPOTIPY_CLIENT_SECRET"]

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/api/register')
def register():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    auth_manager = spotipy.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, 
                                        client_secret=SPOTIPY_CLIENT_SECRET,
                                        redirect_uri=SPOTIPY_REDIRECT_URI,
                                        scope=SPOTIPY_SCOPE, 
                                        cache_path=session_cache_path(),
                                        show_dialog=False)
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    spotify.volume(50)
    spotify.volume(20)
    spotify.volume(100)
    return jsonify({'error_code': '200'})

@app.route('/api/callback')
def callback():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())
    code = request.args.get("code")

    auth_manager = spotipy.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, 
                                        client_secret=SPOTIPY_CLIENT_SECRET,
                                        redirect_uri=SPOTIPY_REDIRECT_URI,
                                        cache_path=session_cache_path(),
                                        scope=SPOTIPY_SCOPE)
    auth_manager.get_access_token(code=code)
    return redirect('/api/register')

@app.route('/sign_out')
def sign_out():
    try:
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/register')

if __name__ == '__main__':
    app.run(threaded=True, port=8080)