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
        print(f"📧 EmailService initialized: {self.sender_email}, Server: {self.smtp_server}:{self.smtp_port}")
        print(f"🔐 Email password set: {'✅ YES' if self.sender_password else '❌ NO'}")

    def send_password_reset_email(self, user_email, reset_link, user_name):
        try:
            # Validasi konfigurasi email lebih ketat
            if not self.sender_email or not self.sender_password:
                print("❌ Email configuration missing: EMAIL_USER or EMAIL_PASSWORD not set")
                return False

            if not self.smtp_server or not self.smtp_port:
                print("❌ SMTP configuration missing")
                return False

            print(f"🔧 Testing SMTP connection to {self.smtp_server}:{self.smtp_port}...")

            subject = "🔐 Reset Password - Kawan UMKM"
            
            # Sederhanakan template email untuk menghindari error
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Reset Password</title>
            </head>
            <body style="font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px;">
                <div style="max-width: 500px; background: white; border-radius: 10px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="background: linear-gradient(135deg, #9B4DFF 0%, #6CECF9 100%); padding: 20px; text-align: center; color: white;">
                        <h1 style="margin: 0; font-size: 24px;">KAWAN UMKM</h1>
                        <p style="margin: 5px 0 0 0;">Reset Password Request</p>
                    </div>
                    <div style="padding: 20px; color: #333; line-height: 1.6;">
                        <h2 style="text-align: center;">Halo {user_name}!</h2>
                        <p style="text-align: center;">Kami menerima permintaan reset password untuk akun Anda.</p>
                        
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="{reset_link}" style="display: inline-block; background: linear-gradient(135deg, #9B4DFF, #6CECF9); color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; font-weight: bold;">
                                🔐 Reset Password
                            </a>
                        </div>
                        
                        <p style="text-align: center; color: #666;">
                            Atau copy link berikut ke browser Anda:
                        </p>
                        <div style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-family: monospace; font-size: 12px; margin: 10px 0;">
                            {reset_link}
                        </div>
                        
                        <p style="text-align: center; font-size: 12px; color: #888;">
                            <strong>⏰ Penting:</strong> Link ini berlaku 1 jam.<br>
                            Abaikan email ini jika Anda tidak meminta reset password.
                        </p>
                    </div>
                    <div style="text-align: center; padding: 15px; color: #666; font-size: 12px; background: #f9f9f9;">
                        <p>&copy; 2024 Kawan UMKM. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
Reset Password - Kawan UMKM

Halo {user_name},

Kami menerima permintaan reset password untuk akun Kawan UMKM Anda.

Silakan klik link berikut untuk reset password:
{reset_link}

Link ini berlaku 1 jam.

Jika Anda tidak meminta reset password, abaikan email ini.

Terima kasih,
Tim Kawan UMKM
            """
            
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Kawan UMKM <{self.sender_email}>"
            msg['To'] = user_email
            msg['Subject'] = subject
            
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            print(f"📤 Attempting to send email to {user_email}...")
            print(f"🔧 SMTP Config: {self.smtp_server}:{self.smtp_port}")
            print(f"🔑 Using email: {self.sender_email}")
            
            # Test connection dengan timeout dan error handling yang lebih baik
            try:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15)
                print("✅ SMTP Connection established")
                
                server.starttls()
                print("✅ TLS started")
                
                # Login dengan error handling
                server.login(self.sender_email, self.sender_password)
                print("✅ SMTP Login successful")
                
                # Send email
                server.send_message(msg)
                print("✅ Email sent successfully")
                
                server.quit()
                print("✅ SMTP connection closed")
                
                print(f"✅ Reset password email sent to {user_email}")
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ SMTP Authentication failed: {str(e)}")
                print("💡 Tips: Pastikan menggunakan App Password bukan password biasa untuk Gmail")
                return False
            except smtplib.SMTPException as e:
                print(f"❌ SMTP Error: {str(e)}")
                return False
            except Exception as e:
                print(f"❌ Connection error: {str(e)}")
                return False
                
        except Exception as e:
            print(f"❌ Unexpected error in send_password_reset_email: {str(e)}")
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
