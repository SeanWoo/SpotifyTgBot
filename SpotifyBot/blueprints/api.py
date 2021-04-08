import uuid
import base64
import json
import requests as r
import datetime, time
from flask import session, request, jsonify, render_template
from flask import Blueprint
from extensions import db
from SpotifyBot import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_SCOPE, QueueRepository, TokenRepository


queueRepository = QueueRepository()
tokenRepository = TokenRepository()

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/callback/<urlid>')

def callback(urlid):
    code = request.args.get("code")

    if code:
        data = queueRepository.get_tgid_by_urlid(urlid)
        
        if not data:
            return jsonify({'error_code': 'not_valid'})

        auth = base64.urlsafe_b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        response = r.post(f"https://accounts.spotify.com/api/token?grant_type=authorization_code&code={code}&scope={SPOTIFY_SCOPE}&redirect_uri={data[2]}",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        })
        tokens = json.loads(response.text)
        
        if tokens.get("access_token") == None:
            return jsonify({'error_code': 'not_valid'})

        tokenRepository.add_token(data[1], tokens["access_token"], tokens["refresh_token"], tokens["expires_in"])

        return render_template('index.html')
    return jsonify({'error_code': 'not_valid'})

