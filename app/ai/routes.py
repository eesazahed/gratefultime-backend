from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from .. import db
from ..models import GratitudeEntry, User
from ..helpers.utils import require_auth, convert_utc_to_local
import requests
from ..config import Config
from cryptography.fernet import Fernet

ai_bp = Blueprint('ai', __name__)


def get_cipher():
    return Fernet(Config.ENCRYPTION_KEY)


def decrypt(token):
    return get_cipher().decrypt(token.encode()).decode()


@ai_bp.route('/monthlysummary', methods=['GET'])
@require_auth
def summarize_month_entries():
    user = db.session.query(User).filter_by(user_id=request.user_id).first()
    if not user or not user.user_timezone:
        return jsonify({'error': 'User or timezone not found'}), 404

    now_utc = datetime.now(timezone.utc)
    try:
        now_user_tz = convert_utc_to_local(now_utc, user.user_timezone)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    start_of_month_user = now_user_tz.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)

    if start_of_month_user.month == 12:
        next_month_user = start_of_month_user.replace(
            year=start_of_month_user.year + 1, month=1)
    else:
        next_month_user = start_of_month_user.replace(
            month=start_of_month_user.month + 1)

    start_utc = start_of_month_user.astimezone(timezone.utc)
    end_utc = next_month_user.astimezone(timezone.utc)

    entries = db.session.query(GratitudeEntry).filter(
        GratitudeEntry.user_id == request.user_id,
        GratitudeEntry.timestamp >= start_utc,
        GratitudeEntry.timestamp < end_utc
    ).order_by(GratitudeEntry.timestamp.asc()).all()

    if not entries:
        return jsonify({'message': 'No entries found for this month'}), 200

    combined_text = ""
    for e in entries:
        try:
            date_local = convert_utc_to_local(
                e.timestamp, user.user_timezone).date()
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        try:
            entry1 = decrypt(e.entry1)
            entry2 = decrypt(e.entry2)
            entry3 = decrypt(e.entry3)
            user_prompt_response = decrypt(e.user_prompt_response)
        except Exception as decrypt_error:
            return jsonify({'error': 'Decryption failed', 'details': str(decrypt_error)}), 500

        combined_text += (
            f"Date: {date_local}\n"
            f"  Gratitude 1: {entry1}\n"
            f"  Gratitude 2: {entry2}\n"
            f"  Gratitude 3: {entry3}\n"
            f"  User Prompt: {e.user_prompt}\n"
            f"  User Response: {user_prompt_response}\n\n"
        )

    prompt = (
        "You are a clear and thoughtful AI. Read the following gratitude journal entries and write a short, powerful summary. "
        "Use simple language. Be direct and meaningful. Highlight the main themes, emotional tone, repeated ideas, and any changes in mindset. "
        "Help the user see their growth and feel understood:\n\n"
        f"{combined_text}"
    )

    api_url = "https://ai.hackclub.com/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that summarizes and analyzes a user's gratitude journal."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to contact AI service', 'details': str(e)}), 503

    ai_response = response.json()

    if "choices" not in ai_response or len(ai_response["choices"]) == 0:
        return jsonify({'error': 'Invalid AI response format'}), 502

    summary = ai_response["choices"][0].get("message", {}).get("content", "")

    return jsonify({'message': 'Monthly summary generated', 'summary': summary})
