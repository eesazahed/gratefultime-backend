from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
import redis

db = SQLAlchemy()


def key_func():
    return getattr(request, 'user_id', get_remote_address())


limiter = Limiter(
    key_func=key_func,
    strategy="fixed-window",
    headers_enabled=True,
    default_limits=["10 per minute"],
    app=None
)


def configure_limiter_storage(app):
    redis_url = f"redis://:{app.config['REDIS_PASSWORD']}@127.0.0.1:{app.config['REDIS_PORT']}"

    print("connecting to redis")

    try:
        pool = redis.connection.BlockingConnectionPool.from_url(
            redis_url, socket_connect_timeout=5)
        client = redis.Redis(connection_pool=pool)
        client.ping()
        limiter.storage_uri = redis_url
        limiter.storage_options = {"connection_pool": pool}
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
        limiter.storage_uri = None
        limiter.storage_options = None


def create_app():
    from .config import Config
    app = Flask(__name__)
    app.config.from_object(Config)

    configure_limiter_storage(app)
    limiter.init_app(app)

    CORS(app)
    db.init_app(app)

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

        @app.route('/api/v1/limiterdata')
        @limiter.exempt
        def limiterdata():
            storage = limiter.storage
            storage_type = type(storage).__name__ if storage else "None"
            return jsonify({'storage_type': storage_type})

        @app.route('/')
        @limiter.exempt
        def index():
            return render_template('index.html', app_id=Config.APP_ID)

    return app
