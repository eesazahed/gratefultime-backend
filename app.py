from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import re

# Initialize app
app = Flask(__name__)
CORS(app)

# Secret key for JWT
SECRET_KEY = "your_super_secret_key"

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gratitude_journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Helpers
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def encode_token(user_id):
    return jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])['user_id']
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

# Models
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    preferred_unlock_time = db.Column(db.Time, default=time(20, 0))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()


# Routes
@app.route('/')
def index():
    return jsonify({'message': 'Server running'})

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get("email", "").strip()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not email or not is_valid_email(email):
        return jsonify({'message': 'Enter a valid email.', 'errorCode': 'email'}), 400
    if not username or len(username) < 3:
        return jsonify({'message': 'Username must be at least 3 characters.', 'errorCode': 'username'}), 400
    if not password or len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters.', 'errorCode': 'password'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered.', 'errorCode': 'email'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already taken.', 'errorCode': 'username'}), 400

    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'token': encode_token(user.user_id)}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not is_valid_email(email):
        return jsonify({'message': 'Enter a valid email.', 'errorCode': 'email'}), 400
    if not password:
        return jsonify({'message': 'Enter your password.', 'errorCode': 'password'}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'User does not exist.', 'errorCode': 'email'}), 404
    if not user.check_password(password):
        return jsonify({'message': 'Invalid password.', 'errorCode': 'password'}), 401

    return jsonify({'token': encode_token(user.user_id)}), 200


@app.route('/entries', methods=['GET'])
@require_auth
def get_entries():
    entries = GratitudeEntry.query.filter_by(user_id=request.user_id).order_by(GratitudeEntry.timestamp.desc()).all()
    return jsonify({
        'message': 'Entries retrieved successfully',
        'data': [{
            'id': e.id,
            'entry1': e.entry1,
            'entry2': e.entry2,
            'entry3': e.entry3,
            'user_prompt': e.user_prompt,
            'user_prompt_response': e.user_prompt_response,
            'timestamp': e.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for e in entries]
    })

@app.route('/entries', methods=['POST'])
@require_auth
def add_entry():
    data = request.get_json()

    if not data.get('entry1'):
        return jsonify({'message': 'Gratitude entry #1 is required.', 'errorCode': 'entry1'}), 400
    if not data.get('entry2'):
        return jsonify({'message': 'Gratitude entry #2 is required.', 'errorCode': 'entry2'}), 400
    if not data.get('entry3'):
        return jsonify({'message': 'Gratitude entry #3 is required.', 'errorCode': 'entry3'}), 400
    if not data.get('user_prompt_response'):
        return jsonify({'message': 'Reflection prompt response is required.', 'errorCode': 'promptResponse'}), 400

    today = datetime.combine(datetime.today(), datetime.min.time())
    existing = GratitudeEntry.query.filter(
        GratitudeEntry.user_id == request.user_id,
        GratitudeEntry.timestamp >= today
    ).first()
    if existing:
        return jsonify({'message': 'Already submitted today.', 'errorCode': 'submission'}), 400

    entry = GratitudeEntry(
        user_id=request.user_id,
        entry1=data['entry1'],
        entry2=data['entry2'],
        entry3=data['entry3'],
        user_prompt=data['user_prompt'],
        user_prompt_response=data['user_prompt_response']
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({'message': 'Entry saved.', 'data': {
        'id': entry.id,
        'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }}), 201

@app.route('/entries/days', methods=['GET'])
@require_auth
def get_entry_days():
    entries = db.session.query(GratitudeEntry.timestamp).filter_by(user_id=request.user_id).distinct().all()
    return jsonify({
        'message': 'Entry days retrieved',
        'data': [e[0].strftime('%Y-%m-%d') for e in entries]
    })

@app.route('/entries/day', methods=['GET'])
@require_auth
def get_entry_by_day():
    date = request.args.get('date')
    if not date:
        return jsonify({'message': 'Date is required'}), 400

    entries = GratitudeEntry.query.filter(
        GratitudeEntry.user_id == request.user_id,
        GratitudeEntry.timestamp.like(f"{date}%")
    ).all()

    return jsonify({
        'message': 'Entries retrieved',
        'data': [{
            'id': e.id,
            'entry1': e.entry1,
            'entry2': e.entry2,
            'entry3': e.entry3,
            'user_prompt': e.user_prompt,
            'user_prompt_response': e.user_prompt_response,
            'timestamp': e.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for e in entries]
    })

@app.route('/entries/<int:id>', methods=['GET'])
@require_auth
def get_entry(id):
    entry = GratitudeEntry.query.get_or_404(id)
    if entry.user_id != request.user_id:
        return jsonify({'message': 'Unauthorized access'}), 403

    return jsonify({'message': 'Entry retrieved', 'data': {
        'id': entry.id,
        'entry1': entry.entry1,
        'entry2': entry.entry2,
        'entry3': entry.entry3,
        'user_prompt': entry.user_prompt,
        'user_prompt_response': entry.user_prompt_response,
        'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }})


@app.route('/entries/<int:id>', methods=['DELETE'])
@require_auth
def delete_entry(id):
    entry = GratitudeEntry.query.get_or_404(id)
    if entry.user_id != request.user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    if entry.timestamp.date() != datetime.today().date():
        return jsonify({'message': 'Can only delete today\'s entry'}), 400

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted'})


# Run server
if __name__ == '__main__':
    app.run(debug=True)
