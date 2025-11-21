import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
from models import db, PasswordResetToken, User
from config import Config
import socket

class EmailService:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.EMAIL_USER
        self.sender_password = Config.EMAIL_PASSWORD
        print(f"📧 EmailService initialized")
        print(f"   SMTP: {self.smtp_server}:{self.smtp_port}")
        print(f"   Email: {self.sender_email}")
        print(f"   Password: {'✅ Set' if self.sender_password else '❌ Missing'}")

    def test_smtp_connection(self):
        """Test koneksi SMTP tanpa mengirim email"""
        try:
            print(f"🧪 Testing SMTP connection to {self.smtp_server}:{self.smtp_port}")
            
            # Test koneksi network dasar
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((self.smtp_server, self.smtp_port))
            sock.close()
            
            if result != 0:
                print(f"❌ Cannot reach {self.smtp_server}:{self.smtp_port}")
                return False
                
            print("✅ Network connection successful")
            return True
            
        except Exception as e:
            print(f"❌ Network test failed: {e}")
            return False

    def send_password_reset_email(self, user_email, reset_link, user_name):
        try:
            # Test koneksi dulu
            if not self.test_smtp_connection():
                return False

            print(f"📤 Preparing email to: {user_email}")

            # Email content yang sangat sederhana
            subject = "Reset Password - Kawan UMKM"
            
            text_content = f"""
Reset Password - Kawan UMKM

Halo {user_name},

Silakan reset password Anda dengan link berikut:
{reset_link}

Link berlaku 1 jam.

Jika Anda tidak meminta reset, abaikan email ini.

Terima kasih,
Tim Kawan UMKM
            """
            
            # Create simple message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = user_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(text_content, 'plain'))
            
            print(f"🔐 Connecting to SMTP...")
            
            # Gunakan approach yang berbeda berdasarkan port
            if self.smtp_port == 465:
                # SSL connection
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=15)
            else:
                # TLS connection
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15)
                server.starttls()
            
            print("✅ SMTP connected")
            
            # Login
            print(f"🔑 Logging in...")
            server.login(self.sender_email, self.sender_password)
            print("✅ Login successful")
            
            # Send email
            server.send_message(msg)
            print("✅ Email sent")
            
            server.quit()
            print("✅ Connection closed")
            
            print(f"🎉 Email successfully sent to {user_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication Failed")
            print(f"   Error: {e}")
            print("💡 Solution: Check App Password and 2FA settings")
            return False
            
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error: {e}")
            return False
            
        except socket.timeout:
            print(f"❌ Connection timeout to {self.smtp_server}:{self.smtp_port}")
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

def create_password_reset_token(user_id):
    """Create and store password reset token"""
    try:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Delete existing tokens
        PasswordResetToken.query.filter_by(user_id=user_id).delete()
        
        # Store new token
        new_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(new_token)
        db.session.commit()
        
        print(f"✅ Reset token created for user {user_id}")
        return token
        
    except Exception as e:
        print(f"❌ Error creating reset token: {e}")
        db.session.rollback()
        return None

def verify_password_reset_token(token):
    """Verify if reset token is valid"""
    try:
        reset_token = PasswordResetToken.query.filter_by(
            token=token, 
            used=False
        ).first()
        
        if not reset_token:
            return None
            
        if reset_token.expires_at < datetime.utcnow():
            return None
            
        return reset_token.user_id
        
    except Exception as e:
        print(f"❌ Error verifying token: {e}")
        return None

def mark_token_used(token):
    """Mark token as used"""
    try:
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if reset_token:
            reset_token.used = True
            db.session.commit()
    except Exception as e:
        print(f"❌ Error marking token used: {e}")
        db.session.rollback()
