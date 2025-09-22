from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from helper import send_gptnew

chat_bp = Blueprint('chat', __name__)

@chat_bp.get('/')
@login_required
def chat_page():
    return render_template('chat.html')

@chat_bp.post('/ask')
@login_required
def ask():
    data = request.get_json(silent=True) or {}
    prompt = (data.get('prompt') or request.form.get('prompt') or '').strip()
    if not prompt:
        return jsonify({'ok': False, 'error': 'Empty prompt'}), 400
    answer = send_gptnew(prompt)
    return jsonify({'ok': True, 'answer': answer})
