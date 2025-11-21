from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from config import Config
from models import db, create_tables
import os
import pymysql

# Import blueprints
from auth import auth_bp
from umkm_routes import umkm_bp
from user_routes import user_bp
from admin_routes import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

# Konfigurasi CORS
CORS(app, 
     origins=[
         "https://kawan-umkm-sekawanpapat.netlify.app",
         "http://localhost:3000",
         "http://localhost:5173"
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True,
     max_age=3600)

# Initialize SQLAlchemy
db.init_app(app)

# Create uploads directory
os.makedirs('uploads/images', exist_ok=True)

# Create tables within app context dengan error handling
with app.app_context():
    try:
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print("💡 Trying to continue without database tables...")

# Register blueprints dengan url_prefix
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(umkm_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# Route untuk health check
@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy', 
            'database': 'connected',
            'service': 'Kawan UMKM API'
        })
    except Exception as e:
        return jsonify({
            'status': 'degraded', 
            'database': 'disconnected',
            'error': str(e),
            'service': 'Kawan UMKM API'
        }), 500

@app.route('/')
def hello():
    return jsonify({
        'message': 'Kawan UMKM Backend API',
        'version': '1.0.0',
        'database': 'MySQL' if 'mysql' in Config.SQLALCHEMY_DATABASE_URI else 'SQLite',
        'endpoints': {
            'auth': '/api/register, /api/login, /api/forgot-password',
            'umkm': '/api/umkm',
            'user': '/api/user/profile, /api/profile',
            'admin': '/api/admin/*'
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Kawan UMKM Backend...")
    print("📊 Database Configuration:")
    print(f"   Type: {'MySQL' if 'mysql' in Config.SQLALCHEMY_DATABASE_URI else 'SQLite'}")
    print(f"   Host: {Config.MYSQL_HOST}")
    print(f"   Database: {Config.MYSQL_DB}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
