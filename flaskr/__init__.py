from flask import Flask
import os

def create_app(config_name):

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://helloFlask:helloFlask@helloflask.c1c3vscy8zzv.us-east-1.rds.amazonaws.com:5432/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY']='frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['UPLOAD_FOLDER'] = 'files/uploads'
    app.config['PROCESSED_FOLDER'] = 'files/processed'

    return app