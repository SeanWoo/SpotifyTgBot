import json, os

path = "config.json" if os.path.exists("config.json") else "config.local.json"

with open(path, "r") as f:
    obj = json.loads(f.read())

    BASE_DOMEN = obj["BASE_DOMEN"]
    REDIRECT_URL = obj["REDIRECT_URL"]

    SPOTIFY_CLIENT_ID = obj["SPOTIFY_CLIENT_ID"]
    SPOTIFY_CLIENT_SECRET = obj["SPOTIFY_CLIENT_SECRET"]
    SPOTIFY_REDIRECT_URI = obj["SPOTIFY_REDIRECT_URI"]
    SPOTIFY_SCOPE = obj["SPOTIFY_SCOPE"]

    TELEGRAM_TOKEN = obj["TELEGRAM_TOKEN"]

    VK_TOKEN = obj['VK_TOKEN']
    ID_GROUP = obj['ID_GROUP']

    DATABASE_CONNECT = obj["DATABASE_CONNECT"]