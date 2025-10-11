import os
from flask import Flask
from flask_cors import CORS
from models import db, BusinessData, DataHistory, QCCIndustry, QCCTech
from routes.data_management import data_bp
from routes.analysis import analysis_bp
import logging
from config import Config

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["https://bsm-frontend.onrender.com"])
logging.basicConfig(level=logging.INFO)

# Load configuration from config.py
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

# Register Blueprints
app.register_blueprint(data_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')






