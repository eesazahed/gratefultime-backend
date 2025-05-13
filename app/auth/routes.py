from flask import Blueprint, request, jsonify
from ..models import User
from .. import db
from ..helpers.utils import encode_token, is_email_taken, verify_apple_token
from ..config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/applelogin', methods=['POST'])
def applelogin():
    data = request.get_json()
    identity_token = data.get("identityToken")
    apple_user_id = data.get("user")
    email = data.get("email", "").strip().lower()
    fullName = data.get("fullName")

    given_name = fullName.get("givenName")
    family_name = fullName.get("familyName")
    full_name_str = f"{given_name} {family_name}" if given_name or family_name else ""

    if not identity_token or not apple_user_id:
        return jsonify({'message': 'Missing Apple identity token or user ID'}), 400

    try:
        payload = verify_apple_token(identity_token)
    except Exception as e:
        return jsonify({'message': 'Invalid identity token', 'error': str(e)}), 401

    token_user_id = payload.get("sub")

    if token_user_id != apple_user_id:
        return jsonify({'message': 'Token user ID mismatch'}), 401

    user = User.query.filter_by(apple_user_id=apple_user_id).first()

    if user:
        if not user.account_active:
            user.account_active = True
            db.session.commit()

    if not user:
        if Config.DEV_MODE:
            user = User(
                email="eszhd@icloud.com",
                username="Eesa Zahed",
                apple_user_id=apple_user_id,
            )
            db.session.add(user)
            db.session.commit()
            return jsonify({'token': encode_token(user.user_id)}), 200

        if not email:
            return jsonify({'message': 'Email required on first Apple login'}), 400

        if is_email_taken(email):
            return jsonify({'message': 'Account conflict. Email already taken'}), 400

        user = User(
            email=email,
            username=full_name_str,
            apple_user_id=apple_user_id,
        )
        db.session.add(user)
        db.session.commit()

    return jsonify({'token': encode_token(user.user_id)}), 200
