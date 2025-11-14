import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
from models import get_db_connection
from config import Config

class EmailService:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.EMAIL_USER
        self.sender_password = Config.EMAIL_PASSWORD
        print(f"📧 EmailService initialized: {self.sender_email}, Server: {self.smtp_server}:{self.smtp_port}")

    def send_password_reset_email(self, user_email, reset_token, user_name):
        try:
            # Create reset link
            reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
            
            # Email content dengan template yang lebih baik
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
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .container {{
                        max-width: 500px;
                        background: white;
                        border-radius: 20px;
                        overflow: hidden;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
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
                        box-shadow: 0 5px 15px rgba(155, 77, 255, 0.3);
                        transition: all 0.3s ease;
                    }}
                    .button:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 8px 25px rgba(155, 77, 255, 0.4);
                    }}
                    .token-box {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                        word-break: break-all;
                        font-family: 'Courier New', monospace;
                        border: 1px dashed #9B4DFF;
                    }}
                    .warning {{
                        background: #fff3cd;
                        border: 1px solid #ffeaa7;
                        padding: 15px;
                        border-radius: 10px;
                        margin: 20px 0;
                        color: #856404;
                    }}
                    .footer {{
                        text-align: center;
                        padding: 30px;
                        color: #666;
                        font-size: 14px;
                        background: #f9f9f9;
                        border-top: 1px solid #e0e0e0;
                    }}
                    .steps {{
                        background: #f8f9ff;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                    }}
                    .step {{
                        display: flex;
                        align-items: center;
                        margin: 10px 0;
                    }}
                    .step-number {{
                        background: #9B4DFF;
                        color: white;
                        width: 25px;
                        height: 25px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 10px;
                        font-size: 14px;
                        font-weight: bold;
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
                        <h2 style="text-align: center; color: #333; margin-bottom: 10px;">Halo {user_name}!</h2>
                        <p style="text-align: center; color: #666; margin-bottom: 30px;">Kami menerima permintaan reset password untuk akun Anda.</p>
                        
                        <div class="steps">
                            <div class="step">
                                <div class="step-number">1</div>
                                <div>Klik tombol reset password di bawah</div>
                            </div>
                            <div class="step">
                                <div class="step-number">2</div>
                                <div>Buat password baru Anda</div>
                            </div>
                            <div class="step">
                                <div class="step-number">3</div>
                                <div>Login dengan password baru</div>
                            </div>
                        </div>
                        
                        <a href="{reset_link}" class="button">🔐 Reset Password Saya</a>
                        
                        <p style="text-align: center; color: #666; margin: 20px 0;">Atau copy link berikut ke browser Anda:</p>
                        
                        <div class="token-box">
                            {reset_link}
                        </div>
                        
                        <div class="warning">
                            <strong>⏰ Penting:</strong> Link ini akan kadaluarsa dalam 1 jam.<br>
                            <strong>🔒 Keamanan:</strong> Jika Anda tidak meminta reset password, abaikan email ini.
                        </div>
                        
                        <p style="text-align: center; margin-top: 30px;">
                            Terima kasih,<br>
                            <strong>Tim Kawan UMKM</strong> 🚀
                        </p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 Kawan UMKM. All rights reserved.</p>
                        <p>Email ini dikirim secara otomatis, mohon tidak membalas email ini.</p>
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
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Kawan UMKM <{self.sender_email}>"
            msg['To'] = user_email
            msg['Subject'] = subject
            
            # Attach both HTML and text versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
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

    def send_review_notification_email(self, umkm_owner_email, umkm_owner_name, umkm_name, reviewer_name, rating, comment, review_date):
        try:
            subject = "📢 Ulasan Baru untuk UMKM Anda - Kawan UMKM"

            # Format rating bintang
            stars = "⭐" * rating + "☆" * (5 - rating)
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 15px;
                        overflow: hidden;
                        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #9B4DFF 0%, #6CECF9 100%);
                        padding: 40px 20px;
                        text-align: center;
                        color: white;
                    }}
                    .logo {{
                        font-size: 32px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }}
                    .content {{
                        padding: 40px;
                        color: #333;
                        line-height: 1.6;
                    }}
                    .review-card {{
                        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
                        border-radius: 12px;
                        padding: 25px;
                        margin: 20px 0;
                        border-left: 4px solid #9B4DFF;
                    }}
                    .rating {{
                        color: #ffc107;
                        font-size: 24px;
                        margin: 10px 0;
                    }}
                    .review-meta {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 15px;
                        padding-bottom: 15px;
                        border-bottom: 1px solid #e0e0e0;
                    }}
                    .reviewer {{
                        font-weight: bold;
                        color: #9B4DFF;
                    }}
                    .review-date {{
                        color: #666;
                        font-size: 14px;
                    }}
                    .comment {{
                        background: white;
                        padding: 15px;
                        border-radius: 8px;
                        border: 1px solid #e0e0e0;
                        font-style: italic;
                    }}
                    .umkm-info {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        padding: 30px;
                        color: #666;
                        font-size: 14px;
                        background: #f9f9f9;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 30px;
                        background: linear-gradient(135deg, #9B4DFF, #6CECF9);
                        color: white;
                        text-decoration: none;
                        border-radius: 25px;
                        margin: 15px 0;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">KAWAN UMKM</div>
                        <p>Notifikasi Ulasan Baru 🎉</p>
                    </div>
                    <div class="content">
                        <h2>Halo {umkm_owner_name},</h2>
                        <p>UMKM Anda <strong>"{umkm_name}"</strong> mendapatkan ulasan baru!</p>
                        
                        <div class="review-card">
                            <div class="review-meta">
                                <div class="reviewer">👤 {reviewer_name}</div>
                                <div class="review-date">📅 {review_date}</div>
                            </div>
                            
                            <div class="rating">
                                {stars}
                                <span style="color: #333; font-size: 16px; margin-left: 10px;">({rating}/5)</span>
                            </div>
                            
                            {comment and f'''
                            <div class="comment">
                                "{comment}"
                            </div>
                            ''' or ''}
                        </div>
                        
                        <div class="umkm-info">
                            <p><strong>📊 Status Ulasan:</strong> Ulasan ini akan tampil di halaman UMKM Anda dan dapat dilihat oleh semua pengunjung.</p>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="http://localhost:3000/umkm" class="button">Lihat UMKM Saya</a>
                        </div>
                        
                        <p>Terima kasih telah menggunakan platform Kawan UMKM! 🚀</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 Kawan UMKM. All rights reserved.</p>
                        <p>Email ini dikirim secara otomatis, mohon tidak membalas email ini.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_content = f"""
            Notifikasi Ulasan Baru - Kawan UMKM
            
            Halo {umkm_owner_name},
            
            UMKM Anda "{umkm_name}" mendapatkan ulasan baru!
            
            👤 Reviewer: {reviewer_name}
            ⭐ Rating: {rating}/5
            📅 Tanggal: {review_date}
            
            Komentar:
            "{comment or 'Tidak ada komentar'}"
            
            Ulasan ini akan tampil di halaman UMKM Anda dan dapat dilihat oleh semua pengunjung.
            
            Terima kasih,
            Tim Kawan UMKM
            """

            msg = MIMEMultipart('alternative')
            msg['From'] = f"Kawan UMKM <{self.sender_email}>"
            msg['To'] = umkm_owner_email
            msg['Subject'] = subject

            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')

            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            print(f"✅ Review notification email sent to {umkm_owner_email}")
            return True

        except Exception as e:
            print(f"❌ Error sending review notification email: {str(e)}")
            return False

def create_password_reset_token(user_id):
    """Create and store password reset token"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Delete any existing tokens for this user
        cursor.execute('DELETE FROM password_reset_tokens WHERE user_id = ?', (user_id,))
        
        # Store new token
        cursor.execute('''
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, token, expires_at))
        
        conn.commit()
        print(f"✅ Reset token created for user {user_id}")
        return token
        
    except Exception as e:
        print(f"❌ Error creating reset token: {e}")
        return None
    finally:
        conn.close()

def verify_password_reset_token(token):
    """Verify if reset token is valid"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id FROM password_reset_tokens 
            WHERE token = ? AND expires_at > datetime('now') AND used = 0
        ''', (token,))
        
        result = cursor.fetchone()
        return result['user_id'] if result else None
        
    except Exception as e:
        print(f"❌ Error verifying token: {e}")
        return None
    finally:
        conn.close()

def mark_token_used(token):
    """Mark token as used"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE password_reset_tokens SET used = 1 WHERE token = ?', (token,))
        conn.commit()
        print(f"✅ Token marked as used: {token}")
    except Exception as e:
        print(f"❌ Error marking token used: {e}")
    finally:
        conn.close()

# Function untuk digunakan di routes (compatibility)
def send_review_notification_email(umkm_owner_email, umkm_owner_name, umkm_name, reviewer_name, rating, comment, review_date):
    """Compatibility function for routes to use"""
    email_service = EmailService()
    return email_service.send_review_notification_email(
        umkm_owner_email, umkm_owner_name, umkm_name, reviewer_name, rating, comment, review_date
    )