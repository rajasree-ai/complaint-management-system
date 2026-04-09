import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://grievance_hub_user:Hge6c5HrVJfKCsIVGjmgiirVyBbKaFlD@dpg-d7b5gb94tr6s73c4ra20-a/grievance_hub')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'apikey'  # SendGrid uses 'apikey' as username
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')  # Set this in Render env vars
    MAIL_DEFAULT_SENDER = 'esec196@gmail.com'  # Verify this in SendGrid