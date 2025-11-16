import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models import db, UMKM, User, Review

umkm_bp = Blueprint('umkm', __name__)

# Create uploads directory
UPLOAD_FOLDER = 'uploads/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes tanpa /api prefix karena sudah ditangani di app.py
@umkm_bp.route('/umkm', methods=['GET', 'POST'])
def handle_umkm():
    if request.method == 'GET':
        return get_all_umkm()
    elif request.method == 'POST':
        return create_umkm()

def get_all_umkm():
    try:
        print("📥 Fetching all UMKM...")
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
        
        print(f"✅ Found {len(result)} UMKM")
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Error fetching UMKM: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def create_umkm():
    try:
        print("📥 Received UMKM creation request")
        print("Files received:", request.files)
        print("Form data:", request.form)
        
        # Check if image file is provided
        if 'image' not in request.files:
            print("❌ No image file in request")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'error': 'No selected file'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use PNG, JPG, JPEG, GIF, or WebP.'}), 400
        
        # Save image
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        print(f"✅ Image saved: {unique_filename}")
        
        # Get form data
        umkm_data = {
            'owner_id': 1,  # Temporary - replace with actual user ID from auth
            'name': request.form.get('name'),
            'category': request.form.get('category'),
            'description': request.form.get('description', ''),
            'image_path': unique_filename,
            'latitude': float(request.form.get('latitude')) if request.form.get('latitude') else None,
            'longitude': float(request.form.get('longitude')) if request.form.get('longitude') else None,
            'address': request.form.get('address'),
            'phone': request.form.get('contact'),
            'hours': request.form.get('hours', '09:00-17:00'),
            'is_approved': True
        }
        
        # Validate required fields
        required_fields = ['name', 'category', 'address', 'phone']
        for field in required_fields:
            if not umkm_data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        print("📝 UMKM data to save:", umkm_data)
        
        # Create UMKM
        new_umkm = UMKM(**umkm_data)
        db.session.add(new_umkm)
        db.session.commit()
        
        print(f"✅ UMKM created successfully: {new_umkm.id}")
        
        # Build response
        umkm_response = {
            'id': new_umkm.id,
            'name': new_umkm.name,
            'category': new_umkm.category,
            'description': new_umkm.description,
            'address': new_umkm.address,
            'contact': new_umkm.phone,
            'image_path': new_umkm.image_path,
            'image_url': f"https://kawan-umkm-backend-production.up.railway.app/api/uploads/images/{new_umkm.image_path}",
            'latitude': new_umkm.latitude,
            'longitude': new_umkm.longitude,
            'hours': new_umkm.hours,
            'avg_rating': 0,
            'review_count': 0,
            'created_at': new_umkm.created_at.isoformat() if new_umkm.created_at else None
        }
        
        return jsonify({
            'message': 'UMKM created successfully',
            'umkm': umkm_response
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating UMKM: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@umkm_bp.route('/umkm/<int:id>', methods=['GET'])
def get_umkm_by_id(id):
    try:
        print(f"🔍 Fetching UMKM with ID: {id}")
        
        umkm = UMKM.query.get(id)
        if not umkm:
            print(f"❌ UMKM with ID {id} not found")
            return jsonify({'error': 'UMKM not found'}), 404
        
        # Calculate average rating and reviews
        reviews = Review.query.filter_by(umkm_id=id).all()
        avg_rating = 0
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
        
        # Build response
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
        
        print(f"✅ UMKM found: {umkm_response['name']}")
        return jsonify(umkm_response)
        
    except Exception as e:
        print(f"❌ Error fetching UMKM {id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@umkm_bp.route('/uploads/images/<filename>')
def serve_image(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(f"❌ Error serving image {filename}: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404

# Endpoint untuk reviews
@umkm_bp.route('/umkm/<int:id>/reviews', methods=['GET'])
def get_umkm_reviews(id):
    try:
        print(f"🔍 Fetching reviews for UMKM {id}")
        reviews = Review.query.filter_by(umkm_id=id).join(User).all()
        
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'user_id': review.user_id,
                'user_name': review.user.name,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat() if review.created_at else None
            })
        
        print(f"✅ Found {len(reviews_data)} reviews")
        return jsonify(reviews_data)
        
    except Exception as e:
        print(f"❌ Error fetching reviews for UMKM {id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@umkm_bp.route('/umkm/<int:id>/reviews', methods=['POST'])
def add_umkm_review(id):
    try:
        data = request.get_json()
        print(f"📥 Adding review for UMKM {id}:", data)
        
        # Validate required fields
        if not data.get('rating') or not data.get('comment'):
            return jsonify({'error': 'Rating and comment are required'}), 400
        
        # In production, get user_id from JWT token
        user_id = 1  # Temporary
        
        new_review = Review(
            umkm_id=id,
            user_id=user_id,
            rating=data['rating'],
            comment=data['comment']
        )
        
        db.session.add(new_review)
        db.session.commit()
        
        print("✅ Review added successfully")
        return jsonify({'message': 'Review added successfully'}), 201
        
    except Exception as e:
        print(f"❌ Error adding review for UMKM {id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
