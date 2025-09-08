import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from models import db, User
from routes.data_management import data_bp
from routes.analysis import analysis_bp
from routes.auth import auth_bp
from flask_login import LoginManager
import logging

instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
db_file = os.path.join(instance_path, 'business_data.db')

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app, supports_credentials=True)
logging.basicConfig(level=logging.INFO)

# Database Configuration
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.logger.info("DATABASE_URL is set, using PostgreSQL.")
    # Ensure the URL starts with postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.logger.info("DATABASE_URL is not set, falling back to SQLite.")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'

app.logger.info(f"Using database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key')
db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
app.register_blueprint(data_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')

# Create database tables within the application context
with app.app_context():
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    db.create_all()
    print("Database has been created with the latest schema.")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
