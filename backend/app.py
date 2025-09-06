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
CORS(app, resources={r"/*": {"origins": "https://bsm-frontend.onrender.com"}}, supports_credentials=True)
logging.basicConfig(level=logging.INFO)

@app.route('/d9a7f8b3-run-admin-fix')
def run_admin_fix():
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            return "User 'admin' not found.", 404
        try:
            admin_user.set_password("1234")
            db.session.add(admin_user)
            db.session.commit()
            return "Admin password has been updated successfully! You can now log in. This temporary URL will be removed.", 200
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {e}", 500

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_file}')
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

@app.cli.command("init-db")
def init_db():
    """Initializes the database."""
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
