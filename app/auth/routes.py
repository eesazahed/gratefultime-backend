from flask import Blueprint, request, jsonify
from ..models import User
from .. import db
from ..helpers.utils import (
    is_valid_email, is_valid_username, encode_token,
    is_email_or_username_taken
)
from sqlalchemy import func

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not is_valid_email(email):
        return jsonify({'message': 'Enter a valid email', 'errorCode': 'email'}), 400
    if not username or len(username) < 3:
        return jsonify({'message': 'Username must be at least 3 characters', 'errorCode': 'username'}), 400
    if not is_valid_username(username):
        return jsonify({'message': 'Username can only contain letters and numbers', 'errorCode': 'username'}), 400
    if not password or len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters', 'errorCode': 'password'}), 400
    if is_email_or_username_taken(email, username):
        if User.query.filter(func.lower(User.email) == email.lower()).first():
            return jsonify({'message': 'Email already registered', 'errorCode': 'email'}), 400
        else:
            return jsonify({'message': 'Username already taken', 'errorCode': 'username'}), 400

    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'token': encode_token(user.user_id)}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not is_valid_email(email):
        return jsonify({'message': 'Enter a valid email', 'errorCode': 'email'}), 400

    user = User.query.filter(func.lower(User.email) == email.lower()).first()
    if not user:
        return jsonify({'message': 'User does not exist', 'errorCode': 'email'}), 404

    if not password:
        return jsonify({'message': 'Enter your password', 'errorCode': 'password'}), 400
    if not user.check_password(password):
        return jsonify({'message': 'Invalid password', 'errorCode': 'password'}), 401

    return jsonify({'token': encode_token(user.user_id)}), 200
