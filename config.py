import os
from urllib.parse import urlparse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Database configuration with improved connection settings
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///complaints.db')
    
    # Fix for Render PostgreSQL
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Optimized engine options for Render free tier
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 1,  # Reduce to 1 to save memory
        'pool_recycle': 280,  # Recycle connections before timeout
        'pool_pre_ping': True,  # Check connection before using
        'pool_timeout': 15,
        'max_overflow': 2,
        'connect_args': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 5,
            'keepalives_count': 3,
            'sslmode': 'require'
        }
    }
    
    # Email settings - disable for now to avoid errors
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('esec196@gmail.com')
    MAIL_PASSWORD = os.environ.get('ezmn vxgj zmly byye')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_USE_SSL = False
    
    # Disable email for now to avoid network errors
    MAIL_SUPPRESS_SEND = True  # This will prevent email sending errors