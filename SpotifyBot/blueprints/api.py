import uuid
import base64
import json
import requests as r
import datetime, time
from flask import session, request, jsonify
from flask import Blueprint
from extensions import db
from SpotifyBot import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_SCOPE


api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/callback/<urlid>')

def callback(urlid):
    code = request.args.get("code")

    if code:
        cursor = db.execute("SELECT * FROM queue WHERE link LIKE %s AND endtime > %s", ('%' + urlid + '%', round(time.time())))
        data = cursor.fetchone()
        db.close_cursor()

        if not data:
            return jsonify({'error_code': 'not_valid'})

        auth = base64.urlsafe_b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        response = r.post(f"https://accounts.spotify.com/api/token?grant_type=authorization_code&code={code}&scope={SPOTIFY_SCOPE}&redirect_uri={data[2]}",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        })
        tokens = json.loads(response.text)
        


        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        db.execute("INSERT INTO tokens(tgid, access_token, refresh_token, expires_in, registration_at) VALUES (%s, %s, %s, %s, %s)",
                (data[1], tokens["access_token"], tokens["refresh_token"], tokens["expires_in"], now))
        db.close_cursor()

        return jsonify({'error_code': 'ok'})
    return jsonify({'error_code': 'not_valid'})

