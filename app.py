from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from models import db, User
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.quiz import quiz_bp
from routes.dashboard import dash_bp

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = 'dev-secret-change-me'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # init db
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # seed a demo user if none exist
        if not User.query.filter_by(email='student@example.com').first():
            User.create_user(email='student@example.com', password='student', is_admin=False)
        if not User.query.filter_by(email='admin@example.com').first():
            User.create_user(email='admin@example.com', password='admin', is_admin=True)

    # login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.signin'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(dash_bp, url_prefix='/dashboard')

    @app.route('/')
    def home():
        # original home stays; “Try now” leads to sign in or chat
        return render_template('index.html', is_authed=current_user.is_authenticated)

    return app

if __name__ == '__main__':
    app = create_app()
    # run on 5000 (not port 80)
    app.run(host='127.0.0.1', port=5000, debug=True)
