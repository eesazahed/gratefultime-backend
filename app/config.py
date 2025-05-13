class Config:
    APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
    APPLE_ISSUER = "https://appleid.apple.com"
    APPLE_AUDIENCE = "host.exp.Exponent"  # todo: replace in production
    SECRET_KEY = 'your_super_secret_key'  # todo: replace in production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///gratitude_journal.db'
    DEV_MODE = True  # todo: turn off in production
