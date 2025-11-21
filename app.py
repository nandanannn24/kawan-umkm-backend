from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db, create_tables
import os
import traceback

# Import blueprints
from auth import auth_bp
from umkm_routes import umkm_bp
from user_routes import user_bp
from admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize CORS
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
    
    # Initialize database
    db.init_app(app)
    
    # Create uploads directory
    os.makedirs('uploads/images', exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(umkm_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    
    # Basic routes
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Kawan UMKM Backend API',
            'status': 'running',
            'version': '1.0.0',
            'database': 'SQLite'
        })
    
    @app.route('/health')
    def health():
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            return jsonify({
                'status': 'healthy', 
                'database': 'SQLite - connected',
                'service': 'Kawan UMKM API'
            })
        except Exception as e:
            return jsonify({
                'status': 'degraded', 
                'database': 'SQLite - error',
                'error': str(e),
                'service': 'Kawan UMKM API'
            }), 500
    
    @app.route('/api/health')
    def api_health():
        return jsonify({'status': 'healthy', 'service': 'Kawan UMKM API'})
    
    # Create tables dengan error handling
    with app.app_context():
        try:
            create_tables()
            print("✅ Database tables initialized successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            print(f"🔍 Stack trace: {traceback.format_exc()}")
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Kawan UMKM Backend on port {port}...")
    print(f"🗄️ Database: SQLite ({Config.SQLITE_DB})")
    app.run(host='0.0.0.0', port=port, debug=False)
