from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import jwt
from config import Config

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    umkms = db.relationship('UMKM', backref='owner', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True, cascade='all, delete-orphan')

class UMKM(db.Model):
    __tablename__ = 'umkm'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    hours = db.Column(db.String(50), default='09:00-17:00')
    is_approved = db.Column(db.Boolean, default=True)  # Set default True untuk development
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='umkm', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='umkm', lazy=True, cascade='all, delete-orphan')

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    umkm_id = db.Column(db.Integer, db.ForeignKey('umkm.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    umkm_id = db.Column(db.Integer, db.ForeignKey('umkm.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint untuk mencegah duplikasi favorite
    __table_args__ = (db.UniqueConstraint('user_id', 'umkm_id', name='unique_user_umkm_favorite'),)

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def hash_password(password):
    """Hash password menggunakan bcrypt"""
    try:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except Exception as e:
        print(f"❌ Error hashing password: {e}")
        raise e

def check_password(password, hashed):
    """Check password terhadap hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        print(f"❌ Error checking password: {e}")
        return False

def create_tables():
    """Create database tables dengan error handling"""
    try:
        print("🔧 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if tables were created
        tables = ['users', 'umkm', 'reviews', 'favorites', 'password_reset_tokens']
        for table in tables:
            try:
                db.session.execute(f"SELECT 1 FROM {table} LIMIT 1")
                print(f"✅ Table {table} exists and accessible")
            except Exception as e:
                print(f"❌ Table {table} error: {e}")
                
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise e

# Fungsi kompatibilitas untuk kode yang sudah ada
def get_db_connection():
    """Helper function for compatibility with existing code"""
    try:
        from config import Config
        import sqlite3
        conn = sqlite3.connect(Config.SQLITE_DB)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Error in get_db_connection: {e}")
        return None
