from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from models import db, create_tables, UMKM, Review
import os
from routes import register_routes

# Import blueprints
from auth import auth_bp
from umkm_routes import umkm_bp
from user_routes import user_bp
from admin_routes import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

# Konfigurasi CORS yang lengkap
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

register_routes(app)

# PERBAIKAN: Tambahkan route langsung untuk /api/umkm
@app.route('/api/umkm', methods=['GET', 'POST', 'OPTIONS'])
def handle_umkm_direct():
    if request.method == 'OPTIONS':
        return '', 200
    elif request.method == 'GET':
        return get_all_umkm_direct()
    elif request.method == 'POST':
        # Forward ke blueprint
        return umkm_bp.create_umkm()

def get_all_umkm_direct():
    try:
        print("📥 [DIRECT] Fetching all UMKM...")
        umkms = UMKM.query.filter_by(is_approved=True).all()
        result = []
        
        for umkm in umkms:
            # Calculate average rating
            reviews = Review.query.filter_by(umkm_id=umkm.id).all()
            avg_rating = 0
            if reviews:
                avg_rating = sum(review.rating for review in reviews) / len(reviews)
            
            result.append({
                'id': umkm.id,
                'name': umkm.name,
                'description': umkm.description,
                'category': umkm.category,
                'address': umkm.address,
                'contact': umkm.phone,
                'image_url': f"https://kawan-umkm-backend-production.up.railway.app/api/uploads/images/{umkm.image_path}",
                'image_path': umkm.image_path,
                'latitude': umkm.latitude,
                'longitude': umkm.longitude,
                'hours': umkm.hours,
                'avg_rating': round(avg_rating, 1),
                'review_count': len(reviews),
                'created_at': umkm.created_at.isoformat() if umkm.created_at else None
            })
        
        print(f"✅ [DIRECT] Found {len(result)} UMKM")
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ [DIRECT] Error fetching UMKM: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# PERBAIKAN: Tambahkan juga route untuk detail UMKM
@app.route('/api/umkm/<int:id>', methods=['GET', 'OPTIONS'])
def get_umkm_by_id_direct(id):
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print(f"🔍 [DIRECT] Fetching UMKM with ID: {id}")
        
        umkm = UMKM.query.get(id)
        if not umkm:
            print(f"❌ [DIRECT] UMKM with ID {id} not found")
            return jsonify({'error': 'UMKM not found'}), 404
        
        # Calculate average rating and reviews
        reviews = Review.query.filter_by(umkm_id=id).all()
        avg_rating = 0
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
        
        umkm_response = {
            'id': umkm.id,
            'name': umkm.name,
            'category': umkm.category,
            'description': umkm.description,
            'address': umkm.address,
            'contact': umkm.phone,
            'phone': umkm.phone,
            'image_path': umkm.image_path,
            'image_url': f"https://kawan-umkm-backend-production.up.railway.app/api/uploads/images/{umkm.image_path}",
            'latitude': umkm.latitude,
            'longitude': umkm.longitude,
            'hours': umkm.hours,
            'owner_name': umkm.owner.name if umkm.owner else 'Tidak diketahui',
            'avg_rating': round(avg_rating, 1),
            'review_count': len(reviews),
            'created_at': umkm.created_at.isoformat() if umkm.created_at else None
        }
        
        print(f"✅ [DIRECT] UMKM found: {umkm_response['name']}")
        return jsonify(umkm_response)
        
    except Exception as e:
        print(f"❌ [DIRECT] Error fetching UMKM {id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Handler untuk after request
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://kawan-umkm-sekawanpapat.netlify.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Route untuk health check
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

# Error handlers
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
    
    # Print registered routes for debugging
    print("🛣️ Registered routes:")
    for rule in app.url_map.iter_rules():
        if 'static' not in rule.rule:
            print(f"  {rule.methods} {rule.rule}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
