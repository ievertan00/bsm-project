import os
from flask import Flask
from flask_cors import CORS
from models import db, User, BusinessData, DataHistory, QCCIndustry, QCCTech
from routes.data_management import data_bp
from routes.analysis import analysis_bp
from routes.auth import auth_bp
from flask_login import LoginManager
import logging
from config import Config

app = Flask(__name__)
CORS(app, supports_credentials=True)
logging.basicConfig(level=logging.INFO)

# Load configuration from config.py
app.config.from_object(Config)

db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-store"
    return response

# Register Blueprints
app.register_blueprint(data_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')





if __name__ == '__main__':
    # Disable reloader to prevent file lock issues during debug
    app.run(debug=True, use_reloader=False)
