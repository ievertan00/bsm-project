import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Get the database URL from environment variables
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///../instance/business_data.db')
    
    # If it's a Supabase URL on the standard port, switch to the PgBouncer port
    if db_url and 'supabase.co:5432' in db_url:
        print("Detected Supabase URL on port 5432, switching to PgBouncer on port 6543 for better compatibility.")
        db_url = db_url.replace(':5432', ':6543')
        
    SQLALCHEMY_DATABASE_URI = db_url
    
    # Add connection pool settings for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 30,
        'connect_args': {
            "options": "-c statement_timeout=30000"  # 30 second timeout
        }
    }
    # Other global settings

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI will be loaded from the environment variable

# Add other environments like TestingConfig if needed
