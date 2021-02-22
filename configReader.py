import json

with open("config.json", "r") as f:
    obj = json.loads(f.read())

    BASE_DOMEN = obj["BASE_DOMEN"]

    SPOTIFY_CLIENT_ID = obj["SPOTIFY_CLIENT_ID"]
    SPOTIFY_CLIENT_SECRET = obj["SPOTIFY_CLIENT_SECRET"]
    SPOTIFY_REDIRECT_URI = obj["SPOTIFY_REDIRECT_URI"]
    SPOTIFY_SCOPE = obj["SPOTIFY_SCOPE"]

    TELEGRAM_TOKEN = obj["TELEGRAM_TOKEN"]

    DATABASE_CONNECT = obj["DATABASE_CONNECT"]