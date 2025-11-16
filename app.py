from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from models import db, create_tables
import os

# Import blueprints
from auth import auth_bp
from umkm_routes import umkm_bp
from user_routes import user_bp
from admin_routes import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

# PERBAIKAN: Konfigurasi CORS yang lebih lengkap
CORS(app, 
     origins=[
         "https://kawan-umkm-sekawanpapat.netlify.app",
         "http://localhost:3000",
         "https://kawan-umkm-backend-production.up.railway.app"
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True,
     max_age=3600)

# Initialize SQLAlchemy
db.init_app(app)

# Create uploads directory
os.makedirs('uploads/images', exist_ok=True)

# Create tables within app context
with app.app_context():
    create_tables()
    print("✅ Database initialized!")

# Register blueprints dengan url_prefix
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(umkm_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# PERBAIKAN: Tambahkan handler untuk OPTIONS method (preflight)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://kawan-umkm-sekawanpapat.netlify.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# PERBAIKAN: Tambahkan route untuk handle OPTIONS preflight
@app.route('/api/umkm', methods=['OPTIONS'])
@app.route('/api/umkm/<int:id>', methods=['OPTIONS'])
@app.route('/api/uploads/images/<filename>', methods=['OPTIONS'])
def options_handler(id=None, filename=None):
    return '', 200

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

# PERBAIKAN: Tambahkan error handler
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(405)
def method_not_allowed(error):
    return {'error': 'Method not allowed'}, 405

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    print("🚀 Starting Kawan UMKM Backend...")
    print("📊 Database: SQLite")
    print("🌐 Server: http://localhost:5000")
    print("🔧 CORS enabled for:", [
        "https://kawan-umkm-sekawanpapat.netlify.app",
        "http://localhost:3000"
    ])
    
    # Print registered routes for debugging
    print("🛣️ Registered routes:")
    for rule in app.url_map.iter_rules():
        if 'static' not in rule.rule:
            print(f"  {rule.methods} {rule.rule}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
