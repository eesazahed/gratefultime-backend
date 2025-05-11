from flask import Blueprint, request, jsonify
from .. import db
from ..models import User, GratitudeEntry
from ..helpers.utils import require_auth, format_timestamp

users_bp = Blueprint('users', __name__)


# GET MOST RECENT ENTRY TIMESTAMP
@users_bp.route('/recententrytimestamp', methods=['GET'])
@require_auth
def get_recent_entry():
    entry = (GratitudeEntry.query
             .filter_by(user_id=request.user_id)
             .order_by(GratitudeEntry.timestamp.desc())
             .first())

    if not entry:
        return jsonify({'message': 'No entries found', 'data': None})

    return jsonify({
        'message': 'Most recent entry retrieved successfully',
        'data': {
            'timestamp': format_timestamp(entry.timestamp)
        }
    })


# GET UNLOCK TIME
@users_bp.route('/unlocktime', methods=['GET'])
@require_auth
def get_unlock_time():
    user = User.query.get_or_404(request.user_id)

    return jsonify({
        'message': 'Preferred unlock time retrieved successfully',
        'data': {
            'preferred_unlock_time': user.preferred_unlock_time
        }
    })


# UPDATE UNLOCK TIME
@users_bp.route('/unlocktime', methods=['PUT'])
@require_auth
def update_unlock_time():
    data = request.get_json()
    user = User.query.get_or_404(request.user_id)

    try:
        unlock_time = int(data['preferred_unlock_time'])

        if unlock_time < 0 or unlock_time > 24:
            return jsonify({'message': 'Unlock time must be between 0 and 24', 'errorCode': 'unlockTime'}), 400
    except ValueError:
        return jsonify({'message': 'Unlock time must be a valid integer', 'errorCode': 'unlockTime'}), 400
    except KeyError:
        return jsonify({'message': 'Unlock time is required', 'errorCode': 'unlockTime'}), 400

    user.preferred_unlock_time = unlock_time
    db.session.commit()

    return jsonify({
        'message': 'Preferred unlock time updated successfully',
        'data': {
            'preferred_unlock_time': user.preferred_unlock_time
        }
    })
