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


# GET USER INFO
@users_bp.route('/info', methods=['GET'])
@require_auth
def get_user_info():
    user = User.query.get_or_404(request.user_id)

    return jsonify({
        'message': 'User information retrieved successfully',
        'data': {
            'user_id': user.user_id,
            'preferred_unlock_time': user.preferred_unlock_time,
            'notifs_on': user.notifs_on
        }
    })


# UPDATE USER SETTINGS
@users_bp.route('/settings', methods=['POST'])
@require_auth
def update_user_settings():
    data = request.get_json()
    user = User.query.get_or_404(request.user_id)

    if 'preferred_unlock_time' in data:
        try:
            unlock_time = int(data['preferred_unlock_time'])

            if unlock_time < 0 or unlock_time > 24:
                return jsonify({'message': 'Unlock time must be between 0 and 24', 'errorCode': 'unlockTime'}), 400
        except ValueError:
            return jsonify({'message': 'Unlock time must be a valid integer', 'errorCode': 'unlockTime'}), 400
        user.preferred_unlock_time = unlock_time

    if 'notifs_on' in data:
        notifs_on = data['notifs_on']

        if not isinstance(notifs_on, bool):
            return jsonify({'message': 'Notifications preference must be a boolean', 'errorCode': 'notifsOn'}), 400
        user.notifs_on = notifs_on

    db.session.commit()

    return jsonify({
        'message': 'User settings updated successfully',
        'data': {
            'preferred_unlock_time': user.preferred_unlock_time,
            'notifs_on': user.notifs_on
        }
    })
