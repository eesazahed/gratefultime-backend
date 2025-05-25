from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded

db = SQLAlchemy()

limiter = Limiter(
    key_func=lambda: getattr(request, 'user_id', get_remote_address()),
    default_limits=["10 per minute"],
    headers_enabled=True
)


def create_app():
    from .config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    limiter.init_app(app)

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(e):
        return jsonify({
            'message': 'Rate limit exceeded',
            'error': 'too_many_requests',
            'status_code': 429
        }), 429

    with app.app_context():
        from .auth.routes import auth_bp
        from .entries.routes import entries_bp
        from .users.routes import users_bp
        from .ai.routes import ai_bp

        app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        app.register_blueprint(entries_bp, url_prefix='/api/v1/entries')
        app.register_blueprint(users_bp, url_prefix='/api/v1/users')
        app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')

        from .models import User, GratitudeEntry
        db.create_all()

        @app.route("/robots.txt")
        @limiter.exempt
        def robots():
            return send_from_directory(app.static_folder, "robots.txt")

        @app.route('/api/v1/')
        @limiter.exempt
        def server():
            return jsonify({'message': 'server running'})

        @app.route('/')
        @limiter.exempt
        def index():
            return render_template('index.html', app_id=Config.APP_ID)

    return app
