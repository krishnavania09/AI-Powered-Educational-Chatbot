from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.get('/signin')
def signin():
    return render_template('signin.html')

@auth_bp.post('/signin')
def signin_post():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        flash('Invalid credentials', 'error')
        return render_template('signin.html'), 200
    login_user(user)
    return redirect(url_for('chat.chat_page'))

@auth_bp.get('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.signin'))
