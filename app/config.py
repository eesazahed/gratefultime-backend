from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
    APPLE_ISSUER = "https://appleid.apple.com"
    APPLE_AUDIENCE = "com.hackclub.gratefultime"
    APP_ID = "no value yet"  # todo: replace in production
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEV_MODE = False
