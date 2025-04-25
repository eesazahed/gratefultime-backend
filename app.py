from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure the app to use SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gratitude_journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the GratitudeEntry model
class GratitudeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # User ID
    entry1 = db.Column(db.String(255), nullable=False)  # First gratitude entry
    entry2 = db.Column(db.String(255), nullable=False)  # Second gratitude entry
    entry3 = db.Column(db.String(255), nullable=False)  # Third gratitude entry
    user_prompt = db.Column(db.String(255), nullable=False)  # User prompt
    user_prompt_response = db.Column(db.String(255), nullable=False)  # User's response to the prompt
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of the entry

    def __repr__(self):
        return f'<GratitudeEntry {self.id}>'

# Create the database tables
with app.app_context():
    db.create_all()

# Route to get all entries
@app.route('/entries', methods=['GET'])
def get_entries():
    entries = GratitudeEntry.query.all()
    return jsonify([{
        'id': entry.id,
        'user_id': entry.user_id,
        'entry1': entry.entry1,
        'entry2': entry.entry2,
        'entry3': entry.entry3,
        'user_prompt': entry.user_prompt,
        'user_prompt_response': entry.user_prompt_response,
        'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp
    } for entry in entries])

# Route to add a new entry
@app.route('/entries', methods=['POST'])
def add_entry():
    data = request.get_json()

    # Validation: Ensure all required fields are provided
    if not all([data.get('user_id'), data.get('entry1'), data.get('entry2'), data.get('entry3'),
                data.get('user_prompt'), data.get('user_prompt_response')]):
        return jsonify({'error': 'user_id, entry1, entry2, entry3, user_prompt, and user_prompt_response are required'}), 400

    # Create the new entry
    new_entry = GratitudeEntry(
        user_id=data['user_id'],
        entry1=data['entry1'],
        entry2=data['entry2'],
        entry3=data['entry3'],
        user_prompt=data['user_prompt'],
        user_prompt_response=data['user_prompt_response'],
    )

    db.session.add(new_entry)
    db.session.commit()

    return jsonify({
        'message': 'Gratitude entry saved successfully',
        'entry': {
            'id': new_entry.id,
            'user_id': new_entry.user_id,
            'entry1': new_entry.entry1,
            'entry2': new_entry.entry2,
            'entry3': new_entry.entry3,
            'user_prompt': new_entry.user_prompt,
            'user_prompt_response': new_entry.user_prompt_response,
            'timestamp': new_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp
        }
    }), 201

# Route to get a specific entry by ID
@app.route('/entries/<int:id>', methods=['GET'])
def get_entry(id):
    entry = GratitudeEntry.query.get_or_404(id)
    return jsonify({
        'id': entry.id,
        'user_id': entry.user_id,
        'entry1': entry.entry1,
        'entry2': entry.entry2,
        'entry3': entry.entry3,
        'user_prompt': entry.user_prompt,
        'user_prompt_response': entry.user_prompt_response,
        'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp
    })

# Route to update a specific entry
@app.route('/entries/<int:id>', methods=['PUT'])
def update_entry(id):
    data = request.get_json()

    # Fetch the entry by ID
    entry = GratitudeEntry.query.get_or_404(id)

    # Ensure required fields are provided
    if not all([data.get('user_id'), data.get('entry1'), data.get('entry2'), data.get('entry3'),
                data.get('user_prompt'), data.get('user_prompt_response')]):
        return jsonify({'error': 'user_id, entry1, entry2, entry3, user_prompt, and user_prompt_response are required'}), 400

    # Update fields if provided
    entry.user_id = data['user_id']
    entry.entry1 = data['entry1']
    entry.entry2 = data['entry2']
    entry.entry3 = data['entry3']
    entry.user_prompt = data['user_prompt']
    entry.user_prompt_response = data['user_prompt_response']

    db.session.commit()

    return jsonify({
        'message': 'Gratitude entry updated successfully',
        'entry': {
            'id': entry.id,
            'user_id': entry.user_id,
            'entry1': entry.entry1,
            'entry2': entry.entry2,
            'entry3': entry.entry3,
            'user_prompt': entry.user_prompt,
            'user_prompt_response': entry.user_prompt_response,
            'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp
        }
    })

# Route to delete a specific entry
@app.route('/entries/<int:id>', methods=['DELETE'])
def delete_entry(id):
    entry = GratitudeEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Gratitude entry deleted successfully'})

# Running the app
if __name__ == '__main__':
    app.run(debug=True)
