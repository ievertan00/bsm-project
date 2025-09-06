from flask import Blueprint, request, jsonify
from models import db, User
from flask_login import login_user, logout_user, login_required, current_user
import logging

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400

        logging.info(f"Attempting to log in user: {username}")
        user = User.query.filter_by(username=username).first()

        if user is None:
            logging.warning(f"Login failed for username: {username}. User not found.")
            return jsonify({'message': 'Invalid username or password'}), 401

        if not user.check_password(password):
            logging.warning(f"Login failed for username: {username}. Incorrect password.")
            return jsonify({'message': 'Invalid username or password'}), 401

        login_user(user)
        logging.info(f"User {username} logged in successfully.")
        return jsonify({'message': 'Logged in successfully'}), 200
    except Exception as e:
        logging.error(f"An error occurred during login: {e}", exc_info=True)
        return jsonify({'message': 'An internal server error occurred.'}), 500

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/profile')
@login_required
def profile():
    return jsonify({'username': current_user.username})

@auth_bp.route('/test_db')
def test_db():
    try:
        db.session.query("1").from_statement(db.text("SELECT 1")).all()
        return jsonify({'message': 'Database connection successful.'}), 200
    except Exception as e:
        logging.error(f"Database connection test failed: {e}", exc_info=True)
        return jsonify({'message': 'Database connection failed.'}), 500
