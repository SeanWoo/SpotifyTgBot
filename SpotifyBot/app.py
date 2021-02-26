import os
import json
from flask import Flask, session, request, redirect, jsonify
from flask_session import Session
from extensions import db, initDb
from SpotifyBot import *
import time

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

def checking_connect_db():
    check_conn = False
    print('New Checking')
    while not check_conn:
        check = db.create_connection(DATABASE_CONNECT["SERVER"], DATABASE_CONNECT["USER"], DATABASE_CONNECT["PASSWORD"], DATABASE_CONNECT["DATABASE"])
        print('Check')
        if check:
            print('Ok')
            check_conn = True
        else:
            print('Error')
            time.sleep(5)
