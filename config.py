import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'grand-royal-hotel-secret-key-2026-super-secure')
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'grand_royal_hotel')
    
    MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    SQLITE_URI = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), 'grand_royal_hotel.db'))}"
    
    # Use SQLite fallback when MySQL is not locally running/installed
    FORCE_MYSQL = os.environ.get('FORCE_MYSQL', 'false').lower() == 'true'
    
    if FORCE_MYSQL:
        SQLALCHEMY_DATABASE_URI = MYSQL_URI
    else:
        # Detect if MySQL is reachable; otherwise use reliable SQLite
        try:
            import pymysql
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                connect_timeout=1
            )
            conn.close()
            SQLALCHEMY_DATABASE_URI = MYSQL_URI
        except Exception:
            SQLALCHEMY_DATABASE_URI = SQLITE_URI
            
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
