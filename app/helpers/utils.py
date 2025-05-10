import re
import jwt
from flask import request, jsonify
from functools import wraps
from datetime import datetime
from ..config import Config
from ..models import User
from sqlalchemy import func


def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)


def is_valid_username(username):
    return re.match(r'^[a-zA-Z0-9]+$', username)


def encode_token(user_id):
    return jwt.encode({'user_id': user_id}, Config.SECRET_KEY, algorithm='HS256')


def decode_token(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])['user_id']
    except:
        return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
        else:
            return jsonify({'message': 'Missing or invalid token'}), 401

        user_id = decode_token(token)
        if not user_id:
            return jsonify({'message': 'Invalid or expired token'}), 401

        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated


def is_email_or_username_taken(email, username):
    return User.query.filter(
        (func.lower(User.email) == email.lower()) |
        (func.lower(User.username) == username.lower())
    ).first()


def format_timestamp(timestamp):
    return timestamp.strftime('%Y-%m-%d %H:%M:%S') + "+00:00"
