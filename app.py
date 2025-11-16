from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from models import db, create_tables  # Import db from models
import os

# Import blueprints
from auth import auth_bp
from umkm_routes import umkm_bp
from user_routes import user_bp
from admin_routes import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy
db.init_app(app)

CORS(app)

# Create uploads directory
os.makedirs('uploads/images', exist_ok=True)

# Create tables within app context
with app.app_context():
    create_tables()

print("✅ Database initialized!")

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(umkm_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

@app.route('/uploads/images/<filename>')
def get_image(filename):
    return send_from_directory('uploads/images', filename)

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'database': 'SQLite'}

@app.route('/')
def hello():
    return {
        'message': 'Kawan UMKM Backend API',
        'version': '1.0.0',
        'database': 'SQLite',
        'endpoints': {
            'auth': '/api/register, /api/login',
            'umkm': '/api/umkm',
            'user': '/api/user/profile, /api/profile',
            'admin': '/api/admin/*'
        }
    }

if __name__ == '__main__':
    print("🚀 Starting Kawan UMKM Backend...")
    print("📊 Database: SQLite")
    print("🌐 Server: http://localhost:5000")
    app.run(debug=True, port=5000)
