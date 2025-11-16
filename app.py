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

# Enable CORS for all routes with specific origins
CORS(app, origins=[
    "https://kawan-umkm.netlify.app", 
    "http://localhost:3000",
    "https://kawan-umkm-backend-production.up.railway.app"
])

# Initialize SQLAlchemy
db.init_app(app)

# Create uploads directory
os.makedirs('uploads/images', exist_ok=True)

# Create tables within app context
with app.app_context():
    create_tables()
    print("✅ Database initialized!")

# PERBAIKAN: Register blueprints hanya sekali dengan prefix yang konsisten
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(umkm_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# PERBAIKAN: Hapus route ini karena sudah ada di umkm_routes.py
# @app.route('/uploads/images/<filename>')
# def get_image(filename):
#     return send_from_directory('uploads/images', filename)

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

# PERBAIKAN: Tambahkan error handler untuk 404
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(405)
def method_not_allowed(error):
    return {'error': 'Method not allowed'}, 405

if __name__ == '__main__':
    print("🚀 Starting Kawan UMKM Backend...")
    print("📊 Database: SQLite")
    print("🌐 Server: http://localhost:5000")
    print("📁 Upload folder:", app.config['UPLOAD_FOLDER'])
    
    # Print registered routes for debugging
    print("🛣️ Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
