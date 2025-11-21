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

    def send_password_reset_email(self, user_email, reset_link, user_name):
        try:
            subject = "🔐 Reset Password - Kawan UMKM"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 500px;
                        background: white;
                        border-radius: 20px;
                        overflow: hidden;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
                        margin: 0 auto;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #9B4DFF 0%, #6CECF9 100%);
                        padding: 40px 30px;
                        text-align: center;
                        color: white;
                    }}
                    .logo {{
                        font-size: 36px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }}
                    .content {{
                        padding: 40px 30px;
                        color: #333;
                        line-height: 1.6;
                    }}
                    .button {{
                        display: block;
                        width: 200px;
                        margin: 30px auto;
                        padding: 15px 30px;
                        background: linear-gradient(135deg, #9B4DFF, #6CECF9);
                        color: white;
                        text-decoration: none;
                        border-radius: 30px;
                        text-align: center;
                        font-weight: bold;
                        font-size: 16px;
                    }}
                    .footer {{
                        text-align: center;
                        padding: 30px;
                        color: #666;
                        font-size: 14px;
                        background: #f9f9f9;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">KAWAN UMKM</div>
                        <p>Reset Password Request</p>
                    </div>
                    <div class="content">
                        <h2 style="text-align: center;">Halo {user_name}!</h2>
                        <p style="text-align: center;">Kami menerima permintaan reset password untuk akun Anda.</p>
                        
                        <a href="{reset_link}" class="button">🔐 Reset Password Saya</a>
                        
                        <p style="text-align: center; color: #666;">
                            Atau copy link berikut ke browser Anda:<br>
                            <code style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all;">{reset_link}</code>
                        </p>
                        
                        <p style="text-align: center;">
                            <strong>⏰ Penting:</strong> Link ini akan kadaluarsa dalam 1 jam.<br>
                            Jika Anda tidak meminta reset password, abaikan email ini.
                        </p>
                    </div>
                    <div class="footer">
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
            
            Link ini akan kadaluarsa dalam 1 jam.
            
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
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Reset password email sent to {user_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email to {user_email}: {str(e)}")
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
            print(f"✅ Token marked as used: {token}")
    except Exception as e:
        print(f"❌ Error marking token used: {e}")
        db.session.rollback()
