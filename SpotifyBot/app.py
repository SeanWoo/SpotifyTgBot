import os
import json
from flask import Flask, session, request, redirect, jsonify
from flask_session import Session
from extensions import db, initDb, userlog
from SpotifyBot import DATABASE_CONNECT, start_telegram_bot, api_blueprint
import time
from loger import get_logger
from .VK.VKBot import start_vk
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(64)
    
    register_extensions(app)
    register_blueprint(app)

    Session(app)
    return app

def register_blueprint(app):
    app.register_blueprint(api_blueprint, url_prefix='/api')

def register_extensions(app):
    checking_connect_db()
    db.create_connection(DATABASE_CONNECT["SERVER"], DATABASE_CONNECT["USER"], DATABASE_CONNECT["PASSWORD"], DATABASE_CONNECT["DATABASE"])
    initDb(db)
    start_telegram_bot()
    start_vk()
def checking_connect_db():
    print('New Checking')
    while True:
        check = db.create_connection(DATABASE_CONNECT["SERVER"], DATABASE_CONNECT["USER"], DATABASE_CONNECT["PASSWORD"], DATABASE_CONNECT["DATABASE"])
        print('Checking connection')
        if check:
            print('Db connected')
            db.close_connection()
            break
        else:
            print('Error connection')
            time.sleep(5)
