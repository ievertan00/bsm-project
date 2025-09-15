from flask import Blueprint, request, jsonify
from models import db, User
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/create_users', methods=['POST'])
def create_users():
    users = [
        {'username': 'tan', 'password': '123'},
        {'username': 'xiao', 'password': '123'},
        {'username': 'liao', 'password': '123'}
    ]
    for user_data in users:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(username=user_data['username'])
            user.set_password(user_data['password'])
            db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Users created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    login_user(user)
    return jsonify({'message': 'Logged in successfully'}), 200

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/profile')
@login_required
def profile():
    return jsonify({'username': current_user.username})
