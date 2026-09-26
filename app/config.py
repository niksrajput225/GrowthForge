import os
import secrets
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR = BASE_DIR / 'app' / 'static' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class BaseConfig:
    """Base configuration for GrowthForge."""
    APP_NAME = "GrowthForge"
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Cookie security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f'sqlite:///{INSTANCE_DIR / "growthforge.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # File Uploads
    UPLOAD_FOLDER = str(UPLOAD_DIR)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day; 50 per hour"
    RATELIMIT_STORAGE_URI = os.environ.get('REDIS_URL') or "memory://"
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    # Production database checks
    if not os.environ.get('SECRET_KEY'):
        # In production, warn or generate persistent token
        pass

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
