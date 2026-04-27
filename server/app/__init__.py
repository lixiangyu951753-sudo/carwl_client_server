from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import os


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    app.config['MONGO_DB'] = os.environ.get('MONGO_DB', 'crawler_db')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'crawler-secret-key-2026')

    mongo_client = MongoClient(app.config['MONGO_URI'])
    app.db = mongo_client[app.config['MONGO_DB']]

    from app.routes.admin import bp as admin_bp
    from app.routes.client import bp as client_bp
    from app.routes.collector import bp as collector_bp

    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(client_bp, url_prefix='/api/client')
    app.register_blueprint(collector_bp)

    return app


app = create_app()
db = app.db
