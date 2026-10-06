import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'carepoint_default_secret_key_change_in_production')
    
    # Database configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'carepoint_hms')
    
    # Security & Session Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Password Reset & Token Settings
    RESET_TOKEN_MAX_AGE_MINUTES = int(os.environ.get('RESET_TOKEN_MAX_AGE_MINUTES', 30))
    
    # SMTP Email Configuration
    SMTP_HOST = os.environ.get('SMTP_HOST', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'True').lower() in ('true', '1', 't')
    SMTP_SENDER = os.environ.get('SMTP_SENDER', 'noreply@carepoint.org')
    
    # Local Development Email Console Fallback (Safely logs reset link to terminal server log ONLY if SMTP is unconfigured)
    DEV_EMAIL_CONSOLE = os.environ.get('DEV_EMAIL_CONSOLE', 'True').lower() in ('true', '1', 't')
