from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
    APPLE_ISSUER = "https://appleid.apple.com"
    APPLE_AUDIENCE = "app.gratefultime"
    APP_ID = "6746601767"
    SECRET_KEY = os.environ['SECRET_KEY']
    ENCRYPTION_KEY = os.environ['ENCRYPTION_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    REDIS_URL = os.environ['REDIS_URL']
    REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEV_MODE = False
