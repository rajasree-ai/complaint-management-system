import os

class Config:
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///complaints.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration for notifications (using Gmail as example)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'esec196@gmail.com'  # Change this
    MAIL_PASSWORD = 'ezmn vxgj zmly byye'      # Change this (use app password)
    MAIL_DEFAULT_SENDER = 'your-email@gmail.com'