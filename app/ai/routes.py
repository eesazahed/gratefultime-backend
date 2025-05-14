from flask import Blueprint, request, jsonify
import requests

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/', methods=['GET'])
def get_prompts():
    return jsonify({"message": "hi"})
