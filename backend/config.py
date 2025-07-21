import os
from dotenv import load_dotenv

# Load environment variables from a .env file
basedir = os.path.abspath(os.path.dirname(__name__))
dotenv_path = os.path.join(basedir, '..', '.env') 
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Other global settings

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI', f"sqlite:///{os.path.join(basedir, '..', 'instance', 'business_data_dev.db')}")

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Ensure you set this in your production environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') 

# Add other environments like TestingConfig if needed
