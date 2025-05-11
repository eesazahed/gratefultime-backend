from flask import Blueprint, request, jsonify
from .. import db
from ..models import User
from ..helpers.utils import require_auth

users_bp = Blueprint('users', __name__)


@users_bp.route('/info', methods=['GET'])
@require_auth
def get_user_info():
    user = User.query.get_or_404(request.user_id)

    return jsonify({
        'message': 'User information retrieved successfully',
        'data': {
            'user_id': user.user_id,
            'email': user.email,
            'username': user.username,
            'preferred_unlock_time': user.preferred_unlock_time
        }
    })


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
