from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()


def create_app():
    from .config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    with app.app_context():
        from .auth.routes import auth_bp
        from .entries.routes import entries_bp
        from .users.routes import users_bp

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(entries_bp, url_prefix='/entries')
        app.register_blueprint(users_bp, url_prefix='/users')

        from .models import User, GratitudeEntry
        db.create_all()

        @app.route('/')
        def index():
            return {'message': 'Server running'}

    return app
