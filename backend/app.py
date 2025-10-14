import os
from flask import Flask
from flask_cors import CORS
from models import db, BusinessData, DataHistory, QCCIndustry, QCCTech
from routes.data_management import data_bp
from routes.analysis import analysis_bp
import logging
from config import Config
import time
import sys

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["https://bsm-frontend.onrender.com"])
logging.basicConfig(level=logging.INFO)

# Load configuration from config.py
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Register Blueprints before creating tables to ensure all models are recognized
app.register_blueprint(data_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')

# Create tables only after app context is established and all blueprints are registered
with app.app_context():
    # Add retry logic for database connection with better error handling
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            db.create_all()
            print("Database tables created successfully!")
            break
        except Exception as e:
            retry_count += 1
            print(f"Attempt {retry_count} failed to create database tables: {e}")
            if retry_count >= max_retries:
                print(f"Failed to connect to database after {max_retries} attempts.")
                print(f"Error details: {str(e)}")
                print("Please ensure your DATABASE_URL environment variable is correctly set with your Supabase connection string.")
                sys.exit(1)  # Exit the application to prevent Render from running a broken service
            else:
                print(f"Retrying in 5 seconds... (Attempt {retry_count + 1} of {max_retries})")
                time.sleep(5)  # Wait 5 seconds before retrying (increased for network issues)






