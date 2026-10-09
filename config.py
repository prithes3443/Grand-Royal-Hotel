import os
from dotenv import load_dotenv

# Base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file
load_dotenv(os.path.join(basedir, '.env'))


def str_to_bool(val, default=False):
    """Safely parse boolean values from environment strings."""
    if val is None:
        return default
    return str(val).strip().lower() in ('true', '1', 't', 'yes', 'y')


class Config:
    """Base Configuration class with environment variable externalization."""
    ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Strict debug toggle: never defaults to True unless FLASK_DEBUG is explicitly enabled
    DEBUG = str_to_bool(os.environ.get('FLASK_DEBUG', 'False'), default=False)
    TESTING = False

    # Application Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        if ENV == 'production':
            raise ValueError(
                "CRITICAL SECURITY ERROR: SECRET_KEY environment variable must be set in production!"
            )
        # Development fallback with clear identification
        SECRET_KEY = 'dev-insecure-key-change-in-production-hotel-pos-2026'

    # CSRF Protection (Flask-WTF)
    WTF_CSRF_ENABLED = str_to_bool(os.environ.get('WTF_CSRF_ENABLED', 'True'), default=True)
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', '3600'))
    WTF_CSRF_CHECK_DEFAULT = True

    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', '3306'))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'grand_royal_hotel')

    # SQLite Local Database File Path
    SQLITE_URI = f"sqlite:///{os.path.join(basedir, 'grand_royal_hotel.db')}"
    
    # Force MySQL Toggle
    FORCE_MYSQL = str_to_bool(os.environ.get('FORCE_MYSQL', 'False'), default=False)

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif FORCE_MYSQL:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    else:
        # Dynamic probe: check if MySQL is running; fallback to SQLite
        try:
            import pymysql
            conn = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                connect_timeout=1
            )
            conn.close()
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        except Exception:
            SQLALCHEMY_DATABASE_URI = SQLITE_URI

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security Cookies & Headers
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = str_to_bool(os.environ.get('SESSION_COOKIE_SECURE', 'False'), default=False)

    # AI & Data Science Configuration
    AI_DEMAND_FORECAST_DAYS = int(os.environ.get('AI_DEMAND_FORECAST_DAYS', '7'))
    AI_RECOMMENDER_TOP_N = int(os.environ.get('AI_RECOMMENDER_TOP_N', '4'))
    AI_DYNAMIC_PRICING_ENABLED = str_to_bool(os.environ.get('AI_DYNAMIC_PRICING_ENABLED', 'True'), default=True)


class DevelopmentConfig(Config):
    """Development configuration with debugging enabled."""
    DEBUG = str_to_bool(os.environ.get('FLASK_DEBUG', 'True'), default=True)


class ProductionConfig(Config):
    """Production configuration with strict security and debug off."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration with in-memory database and test settings."""
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False  # Disabled by default in tests for business logic testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key-grand-royal-hotel'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}
