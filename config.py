import os
from urllib.parse import urlparse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Database configuration with connection pooling fixes
    database_url = os.environ.get('DATABASE_URL', 'postgresql://root:I9rwqy3xDnTBGHgGaW4KhaUlpCuiNMFp@dpg-d74j9594tr6s73cq90l0-a/complaints_3nry')
    
    # Fix for Render PostgreSQL
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Add connection pool settings to prevent timeout
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 10,
        'connect_args': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    }
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('esec196@gmail.com')
    MAIL_PASSWORD = os.environ.get('ezmn vxgj zmly byye')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')