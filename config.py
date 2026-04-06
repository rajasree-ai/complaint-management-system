import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///complaints.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration - Try different ports
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))  # Try 465 instead of 587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'True').lower() == 'true'  # Use SSL for port 465
    MAIL_USERNAME = os.environ.get('esec196@gmail.com')
    MAIL_PASSWORD = os.environ.get('kidu kxjr pfwc gobj')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')