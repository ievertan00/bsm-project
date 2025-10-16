import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, BusinessData, DataHistory, QCCIndustry, QCCTech
from routes.data_management import data_bp
from routes.analysis import analysis_bp
import logging
from config import Config
import time
import sys

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["*"])
logging.basicConfig(level=logging.INFO)

# Load configuration from config.py
app.config.from_object(Config)

# Initialize database
db.init_app(app)
migrate = Migrate(app, db)

# Health check endpoint
@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return {"status": "healthy", "database": "connected"}, 200
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}, 500

# Register Blueprints (add them before attempting to create tables)
app.register_blueprint(data_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')

# Only create tables after app context is established
with app.app_context():
    # Add retry logic for database connection with better error handling
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Test the connection without creating tables first
            db.engine.connect()
            print("Database connection established successfully!")
            # Create tables if connection is successful
            db.create_all()
            print("Database tables created successfully!")
            break
        except Exception as e:
            retry_count += 1
            print(f"Attempt {retry_count} failed to connect to database: {e}")
            if retry_count >= max_retries:
                print(f"Failed to connect to database after {max_retries} attempts.")
                print(f"Error details: {str(e)}")
                print("Please ensure your DATABASE_URL environment variable is correctly set with your Supabase connection string")
                print("and that your Supabase database allows connections from Render's IP addresses.")
                sys.exit(1)  # Exit the application to prevent Render from running a broken service
            else:
                print(f"Retrying in 5 seconds... (Attempt {retry_count + 1} of {max_retries})")
                time.sleep(5)  # Wait 5 seconds before retrying (increased for network issues)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)