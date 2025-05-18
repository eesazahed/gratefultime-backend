import jwt
import requests
from flask import request, jsonify
from functools import wraps
from jwt.algorithms import RSAAlgorithm
from jwt import get_unverified_header
from sqlalchemy import func
from ..config import Config
from ..models import User
import datetime
import pytz
import json


def format_timestamp(timestamp):
    return timestamp.strftime('%Y-%m-%d %H:%M:%S') + "+00:00"


def encode_token(user_id):
    token = jwt.encode({'user_id': user_id},
                       Config.SECRET_KEY, algorithm='HS256')
    return token.decode('utf-8') if isinstance(token, bytes) else token


def decode_token(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])['user_id']
    except:
        return None


def is_email_taken(email):
    return User.query.filter(func.lower(User.email) == email.lower()).first()


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


def get_public_key_from_apple(kid):
    response = requests.get(Config.APPLE_KEYS_URL)
    if response.status_code != 200:
        raise Exception("Failed to fetch Apple public keys")

    keys = response.json().get("keys", [])
    key = next((k for k in keys if k["kid"] == kid), None)
    if not key:
        raise Exception("No key found with matching kid")

    key_json = json.dumps(key)
    return RSAAlgorithm.from_jwk(key_json)


def verify_apple_token(identity_token):
    header = get_unverified_header(identity_token)
    public_key = get_public_key_from_apple(header["kid"])

    return jwt.decode(
        identity_token,
        public_key,
        algorithms=["RS256"],
        audience=Config.APPLE_AUDIENCE,
        issuer=Config.APPLE_ISSUER,
        leeway=datetime.timedelta(seconds=300)
    )


def convert_utc_to_local(utc_dt, timezone_str):
    if timezone_str not in pytz.all_timezones:
        raise ValueError(f"Invalid timezone: {timezone_str}")

    local_tz = pytz.timezone(timezone_str)
    utc_dt = utc_dt.replace(tzinfo=pytz.utc)
    local_dt = utc_dt.astimezone(local_tz)
    return local_dt
