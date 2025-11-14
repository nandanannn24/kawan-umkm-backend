import os
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv()

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLITE_DB = os.path.join(BASEDIR, 'kawan_umkm.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-here')
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'uploads', 'images')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024 
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Email configuration
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Test email configuration
        print("📧 Email Configuration:")
        print(f"   EMAIL_USER: {Config.EMAIL_USER}")
        print(f"   SMTP_SERVER: {Config.SMTP_SERVER}")
        print(f"   SMTP_PORT: {Config.SMTP_PORT}")
        print(f"   EMAIL_PASSWORD: {'✅ SET' if Config.EMAIL_PASSWORD else '❌ MISSING'}")