import uuid
import requests as r
from flask import session, request, jsonify
from flask import Blueprint
from extensions import db
from SpotifyBot import BASE_DOMEN

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/callback')

def callback():
    code = request.args.get("code")

    access_token = request.args.get("access_token")
    token_type = request.args.get("token_type")
    scope = request.args.get("scope")
    expires_in = request.args.get("expires_in")
    refresh_token = request.args.get("refresh_token")

    if code:
        response = r.post(f"https://accounts.spotify.com/api/token?grant_type=authorization_code&code={code}&redirect_uri={BASE_DOMEN}/api/callback")

    if access_token and refresh_token:
        pass
        #TODO: сделать добавление в базу данных токенов

    return jsonify({'error_code': 'ok'})



