import secrets
import hashlib
import smtplib
import logging
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from werkzeug.security import generate_password_hash
from database.connection import get_db_cursor
from config import Config
from mysql.connector import Error

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def create_reset_token(user_id):
        """
        Generate a cryptographically secure random token, store its SHA-256 hash in MySQL,
        and return the raw unhashed token for reset URL construction.
        """
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        expires_at = datetime.now(timezone.utc).astimezone().replace(tzinfo=None) + timedelta(minutes=Config.RESET_TOKEN_MAX_AGE_MINUTES)
        
        with get_db_cursor(commit=True) as cursor:
            # Mark previous active reset tokens for this user as expired
            cursor.execute("""
                UPDATE password_resets 
                SET used_at = NOW() 
                WHERE user_id = %s AND used_at IS NULL
            """, (user_id,))
            
            cursor.execute("""
                INSERT INTO password_resets (user_id, token_hash, expires_at, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (user_id, token_hash, expires_at))
            
        return raw_token

    @staticmethod
    def validate_reset_token(raw_token):
        """
        Validate token by matching SHA-256 hash against active non-expired records.
        """
        if not raw_token:
            return False, "Invalid reset token."
            
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT pr.id, pr.user_id, pr.expires_at, pr.used_at, u.username, u.email 
                FROM password_resets pr
                JOIN users u ON pr.user_id = u.id
                WHERE pr.token_hash = %s
            """, (token_hash,))
            record = cursor.fetchone()
            
            if not record:
                return False, "Invalid or unrecognized password reset token."
            if record['used_at'] is not None:
                return False, "This password reset link has already been used. Please request a new one."
                
            # Expiration check
            if record['expires_at'] < datetime.now():
                return False, "This password reset link has expired (valid for 30 minutes). Please request a new one."
                
            return True, record

    @staticmethod
    def reset_password(raw_token, new_password):
        """
        Atomically update user's password hash and mark token as consumed.
        """
        is_valid, result = AuthService.validate_reset_token(raw_token)
        if not is_valid:
            return False, result
            
        record = result
        new_password_hash = generate_password_hash(new_password)
        
        with get_db_cursor(commit=False) as cursor:
            try:
                # 1. Update user's password
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = %s 
                    WHERE id = %s
                """, (new_password_hash, record['user_id']))
                
                # 2. Mark token as consumed
                cursor.execute("""
                    UPDATE password_resets 
                    SET used_at = NOW() 
                    WHERE id = %s
                """, (record['id'],))
                
                cursor.execute("COMMIT")
                return True, "Your password has been reset successfully. You may now log in."
            except Error as err:
                cursor.execute("ROLLBACK")
                return False, f"Password reset failed: {str(err)}"

    @staticmethod
    def send_reset_email(to_email, reset_url):
        """
        Send password recovery email via SMTP. Fall back to secure local console logging in development mode.
        """
        subject = "CarePoint HMS - Password Reset Request"
        body = f"""Hello,

A password reset request was submitted for your CarePoint Hospital Management System account.

To reset your password, please click the link below (or copy and paste it into your browser):
{reset_url}

Note: This recovery link is single-use and will expire in {Config.RESET_TOKEN_MAX_AGE_MINUTES} minutes.

If you did not request a password reset, please ignore this email or contact system administration.

Regards,
CarePoint HMS Security Team
"""

        # Check if SMTP configuration is present
        if Config.SMTP_HOST and Config.SMTP_USER and Config.SMTP_PASSWORD:
            try:
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = Config.SMTP_SENDER
                msg['To'] = to_email
                msg.set_content(body)
                
                if Config.SMTP_USE_TLS:
                    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as server:
                        server.starttls()
                        server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as server:
                        server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                        server.send_message(msg)
                        
                logger.info(f"Password reset email sent successfully via SMTP to {to_email}")
                return True
            except Exception as e:
                logger.error(f"Failed to deliver SMTP password reset email to {to_email}: {e}")
                # Fallthrough to dev log if enabled
                
        if Config.DEV_EMAIL_CONSOLE:
            logger.info("="*70)
            logger.info("[DEV EMAIL CONSOLE MODE] Password Reset Link Generated:")
            logger.info(f"Recipient: {to_email}")
            logger.info(f"Reset URL: {reset_url}")
            logger.info("="*70)
            return True
            
        return False
