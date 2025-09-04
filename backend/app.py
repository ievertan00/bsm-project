import os
from flask import Flask
from flask_cors import CORS
from models import db
from routes.data_management import data_bp
from routes.analysis import analysis_bp
import logging

instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
db_file = os.path.join(instance_path, 'business_data.db')

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'you-will-never-guess'
db.init_app(app)

# Register Blueprints
app.register_blueprint(data_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')

# Create database tables within the application context
with app.app_context():
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    db.create_all()
    print("Database has been created with the latest schema.")

if __name__ == '__main__':
    # Disable reloader to prevent file lock issues during debug
    app.run(debug=True, use_reloader=False)
