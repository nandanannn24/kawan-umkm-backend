import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite configuration
    SQLITE_DB = os.path.join(BASEDIR, 'kawan_umkm.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-here-change-this-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here-change-this-in-production')
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'uploads', 'images')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024 
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Email configuration
    EMAIL_USER = os.getenv('EMAIL_USER', 'sekawanpapat.umkm@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'qlmr qafm nkvp ufgs')
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
        
        # Test database configuration
        print("🗄️ Database Configuration:")
        print(f"   Database: SQLite")
        print(f"   Database File: {Config.SQLITE_DB}")
