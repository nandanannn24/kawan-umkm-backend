from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

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
    umkms = db.relationship('UMKM', backref='owner', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

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
    hours = db.Column(db.String(50))
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='umkm', lazy=True)
    favorites = db.relationship('Favorite', backref='umkm', lazy=True)

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

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_tables():
    print("🔧 Creating database tables...")
    db.create_all()
    print("✅ Database tables created!")

# Tambahkan fungsi helper untuk kompatibilitas
def get_db_connection():
    """Helper function for compatibility with existing code"""
    import sqlite3
    from config import Config
    conn = sqlite3.connect(Config.SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn

# Password reset token functions (simplified)
def create_password_reset_token(user_id):
    """Create password reset token - simplified version"""
    import uuid
    return str(uuid.uuid4())

def verify_password_reset_token(token):
    """Verify password reset token - simplified version"""
    # For now, return a dummy user ID
    return 1

def mark_token_used(token):
    """Mark token as used - simplified version"""
    pass

# Email service placeholder
class EmailService:
    def send_password_reset_email(self, email, token, name):
        print(f"📧 Password reset email would be sent to: {email}")
        print(f"🔑 Token: {token}")
        return True
