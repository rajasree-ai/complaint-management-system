import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///complaints.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration (Gmail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('esec196@gmail.com')  # Your Gmail
    MAIL_PASSWORD = os.environ.get('kidu kxjr pfwc gobj')  # Your App Password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')