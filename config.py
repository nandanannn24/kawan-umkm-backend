import os
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv()

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # MySQL configuration dari environment variables
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'kawan_umkm')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    
    # SQLAlchemy configuration - gunakan MySQL
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Untuk backward compatibility (jika masih perlu SQLite)
    SQLITE_DB = os.path.join(BASEDIR, 'kawan_umkm.db')
    
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
        print(f"   MYSQL_HOST: {Config.MYSQL_HOST}")
        print(f"   MYSQL_USER: {Config.MYSQL_USER}")
        print(f"   MYSQL_DB: {Config.MYSQL_DB}")
        print(f"   MYSQL_PORT: {Config.MYSQL_PORT}")
        print(f"   MYSQL_PASSWORD: {'✅ SET' if Config.MYSQL_PASSWORD else '❌ MISSING'}")
