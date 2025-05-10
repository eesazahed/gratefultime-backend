from . import db
from datetime import datetime, time, timezone
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    preferred_unlock_time = db.Column(db.Time, default=time(20, 0))
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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
