from flask import Flask
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/'
app.config['MONGO_DB'] = 'crawler_db'
app.config['SECRET_KEY'] = 'crawler-secret-key-2026'

mongo_client = MongoClient(app.config['MONGO_URI'])
db = mongo_client[app.config['MONGO_DB']]

from app.routes import client, admin
app.register_blueprint(client.bp, url_prefix='/api/client')
app.register_blueprint(admin.bp, url_prefix='/api')
