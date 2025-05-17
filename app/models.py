from . import db
from datetime import datetime, timezone


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(128), unique=True, nullable=True)
    user_timezone = db.Column(db.String(64), nullable=True)
    apple_user_id = db.Column(db.String(255), unique=True, nullable=True)
    preferred_unlock_time = db.Column(db.Integer, default=20)
    account_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.now(timezone.utc))


class GratitudeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    entry1 = db.Column(db.String(255), nullable=False)
    entry2 = db.Column(db.String(255), nullable=False)
    entry3 = db.Column(db.String(255), nullable=False)
    user_prompt = db.Column(db.String(255), nullable=False)
    user_prompt_response = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True),
                          default=datetime.now(timezone.utc))
