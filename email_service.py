import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
from models import db, PasswordResetToken, User
from config import Config

class EmailService:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.EMAIL_USER
        self.sender_password = Config.EMAIL_PASSWORD
        print(f"📧 EmailService initialized: {self.sender_email}")
        print(f"🔧 SMTP Server: {self.smtp_server}:{self.smtp_port}")

    def send_password_reset_email(self, user_email, reset_link, user_name):
        try:
            # Validasi konfigurasi email
            if not all([self.sender_email, self.sender_password, self.smtp_server]):
                print("❌ Email configuration missing")
                return False

            print(f"📤 Preparing to send email to: {user_email}")

            subject = "🔐 Reset Password - Kawan UMKM"
            
            # Template email yang lebih sederhana
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center; color: white;">
                    <h1>KAWAN UMKM</h1>
                    <p>Reset Password Request</p>
                </div>
                <div style="padding: 20px; background: white;">
                    <h2>Halo {user_name}!</h2>
                    <p>Kami menerima permintaan reset password untuk akun Anda.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p>Atau copy link berikut ke browser Anda:</p>
                    <div style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-family: monospace;">
                        {reset_link}
                    </div>
                    
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">
                        <strong>Penting:</strong> Link ini berlaku 1 jam.<br>
                        Jika Anda tidak meminta reset password, abaikan email ini.
                    </p>
                </div>
                <div style="background: #f9f9f9; padding: 15px; text-align: center; color: #666; font-size: 12px;">
                    <p>&copy; 2024 Kawan UMKM. All rights reserved.</p>
                </div>
            </div>
            """
            
            text_content = f"""
Reset Password - Kawan UMKM

Halo {user_name},

Kami menerima permintaan reset password untuk akun Anda.

Silakan klik link berikut untuk reset password:
{reset_link}

Link ini berlaku 1 jam.

Jika Anda tidak meminta reset password, abaikan email ini.

Terima kasih,
Tim Kawan UMKM
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Kawan UMKM <{self.sender_email}>"
            msg['To'] = user_email
            msg['Subject'] = subject
            
            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            print(f"🔐 Attempting SMTP connection to {self.smtp_server}:{self.smtp_port}")
            
            # Create SMTP connection dengan timeout
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=20)
            
            # Debug: Test connection
            print("✅ SMTP connection established")
            
            # Start TLS
            server.starttls()
            print("✅ TLS encryption started")
            
            # Login
            print(f"🔑 Attempting login with: {self.sender_email}")
            server.login(self.sender_email, self.sender_password)
            print("✅ Login successful")
            
            # Send email
            server.send_message(msg)
            print("✅ Email sent successfully")
            
            # Close connection
            server.quit()
            print("✅ SMTP connection closed")
            
            print(f"🎉 Password reset email successfully sent to {user_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication Failed: {str(e)}")
            print("💡 Tips for Gmail:")
            print("   1. Pastikan 2-Factor Authentication aktif")
            print("   2. Gunakan App Password, bukan password biasa")
            print("   3. App Password bisa dibuat di: https://myaccount.google.com/apppasswords")
            return False
            
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error: {str(e)}")
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            import traceback
            print(f"🔍 Stack trace: {traceback.format_exc()}")
            return False

def create_password_reset_token(user_id):
    """Create and store password reset token"""
    try:
        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Delete any existing tokens for this user
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
            print(f"❌ Token not found or already used: {token}")
            return None
            
        if reset_token.expires_at < datetime.utcnow():
            print(f"❌ Token expired: {token}")
            return None
            
        print(f"✅ Token valid for user {reset_token.user_id}")
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
            print(f"✅ Token marked as used: {token}")
    except Exception as e:
        print(f"❌ Error marking token used: {e}")
        db.session.rollback()
