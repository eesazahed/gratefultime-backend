from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from .. import db
from ..models import GratitudeEntry, User
from ..helpers.utils import require_auth, format_timestamp

entries_bp = Blueprint('entries', __name__)


# GETS ENTRIES WITH PAGINATION
@entries_bp.route('', methods=['GET'])
@require_auth
def get_entries():
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))

    total_entries = GratitudeEntry.query.filter_by(
        user_id=request.user_id).count()
    query = GratitudeEntry.query.filter_by(
        user_id=request.user_id).order_by(GratitudeEntry.timestamp.desc())
    entries = query.offset(offset).limit(limit).all()
    next_offset = offset + limit if offset + limit < total_entries else None

    return jsonify({
        'message': 'Entries retrieved successfully',
        'data': [{
            'id': e.id,
            'entry1': e.entry1,
            'entry2': e.entry2,
            'entry3': e.entry3,
            'user_prompt': e.user_prompt,
            'user_prompt_response': e.user_prompt_response,
            'timestamp': format_timestamp(e.timestamp)
        } for e in entries],
        'nextOffset': next_offset
    })


# SUBMITS AN ENTRY
@entries_bp.route('', methods=['POST'])
@require_auth
def add_entry():
    user = User.query.filter_by(user_id=request.user_id).first()
    if not user or not user.account_active:
        return jsonify({'message': 'Your account is inactive', 'errorCode': 'submission'}), 403

    data = request.get_json()

    if not data.get('entry1'):
        return jsonify({'message': 'Entry is required', 'errorCode': 'entry1'}), 400
    if len(data['entry1']) > 50:
        return jsonify({'message': 'Entry must be 50 characters or fewer', 'errorCode': 'entry1'}), 400

    if not data.get('entry2'):
        return jsonify({'message': 'Entry is required', 'errorCode': 'entry2'}), 400
    if len(data['entry2']) > 50:
        return jsonify({'message': 'Entry must be 50 characters or fewer', 'errorCode': 'entry2'}), 400

    if not data.get('entry3'):
        return jsonify({'message': 'Entry is required', 'errorCode': 'entry3'}), 400
    if len(data['entry3']) > 50:
        return jsonify({'message': 'Entry must be 50 characters or fewer', 'errorCode': 'entry3'}), 400

    if not data.get('user_prompt_response'):
        return jsonify({'message': 'Reflection prompt response is required', 'errorCode': 'promptResponse'}), 400
    if len(data['user_prompt_response']) > 100:
        return jsonify({'message': 'Reflection prompt response must be 100 characters or fewer', 'errorCode': 'promptResponse'}), 400

    today = datetime.combine(datetime.now(timezone.utc), datetime.min.time())

    if GratitudeEntry.query.filter(
        GratitudeEntry.user_id == request.user_id,
        GratitudeEntry.timestamp >= today
    ).first():
        return jsonify({'message': 'Already submitted today', 'errorCode': 'submission'}), 400

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

    return jsonify({'message': 'Entry saved', 'data': {
        'id': entry.id,
        'timestamp': format_timestamp(entry.timestamp)
    }}), 201


# GETS ALL THE DAYS THAT A USER HAS CREATED AN ENTRY
@entries_bp.route('/days', methods=['GET'])
@require_auth
def get_entry_days():
    entries = db.session.query(GratitudeEntry.timestamp).filter_by(
        user_id=request.user_id).distinct().all()

    return jsonify({'message': 'Entry days retrieved', 'data': [format_timestamp(e[0]) for e in entries]})


# GET A SPECIFIC DAY
@entries_bp.route('/day', methods=['GET'])
@require_auth
def get_entry_by_day():
    date = request.args.get('date')
    if not date:
        return jsonify({'message': 'Date is required'}), 400

    yyyy_mm_dd = datetime.fromisoformat(date).date()

    entry = GratitudeEntry.query.filter(
        GratitudeEntry.user_id == request.user_id,
        GratitudeEntry.timestamp.like(f"{yyyy_mm_dd}%")
    ).first_or_404()

    return jsonify({'message': 'entry retrieved', 'data': {
        'id': entry.id,
        'entry1': entry.entry1,
        'entry2': entry.entry2,
        'entry3': entry.entry3,
        'user_prompt': entry.user_prompt,
        'user_prompt_response': entry.user_prompt_response,
        'timestamp': format_timestamp(entry.timestamp)
    }})


# GET A SPECIFIC ENTRY BY ID
@entries_bp.route('/<int:id>', methods=['GET'])
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
        'timestamp': format_timestamp(entry.timestamp)
    }})


# DELETE A SPECIFIC ENTRY
@entries_bp.route('/<int:id>', methods=['DELETE'])
@require_auth
def delete_entry(id):
    entry = GratitudeEntry.query.get_or_404(id)
    if entry.user_id != request.user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    if entry.timestamp.date() != datetime.now(timezone.utc).date():
        return jsonify({'message': 'Can only delete today\'s entry'}), 400

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted'})
