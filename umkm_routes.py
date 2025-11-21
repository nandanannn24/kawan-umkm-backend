import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models import db, UMKM, User, Review
import jwt
from config import Config

umkm_bp = Blueprint('umkm', __name__)

# Create uploads directory
UPLOAD_FOLDER = 'uploads/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk verifikasi token
def get_current_user():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return None
    
    try:
        token = token[7:]
        data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return User.query.get(data['user_id'])
    except:
        return None

# Routes
@umkm_bp.route('/umkm', methods=['GET', 'POST', 'OPTIONS'])
def handle_umkm():
    if request.method == 'GET':
        return get_all_umkm()
    elif request.method == 'POST':
        return create_umkm()
    elif request.method == 'OPTIONS':
        return '', 200

def get_all_umkm():
    try:
        print("📥 Fetching all UMKM...")
        umkms = UMKM.query.filter_by(is_approved=True).all()
        result = []
        
        for umkm in umkms:
            reviews = Review.query.filter_by(umkm_id=umkm.id).all()
            avg_rating = 0
            if reviews:
                avg_rating = sum(review.rating for review in reviews) / len(reviews)
            
            base_url = request.host_url.rstrip('/')
            image_url = f"{base_url}api/uploads/images/{umkm.image_path}" if umkm.image_path else None
            
            result.append({
                'id': umkm.id,
                'name': umkm.name,
                'description': umkm.description,
                'category': umkm.category,
                'address': umkm.address,
                'contact': umkm.phone,
                'image_url': image_url,
                'image_path': umkm.image_path,
                'latitude': umkm.latitude,
                'longitude': umkm.longitude,
                'hours': umkm.hours,
                'avg_rating': round(avg_rating, 1),
                'review_count': len(reviews),
                'owner_id': umkm.owner_id,
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
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if 'image' not in request.files:
            print("❌ No image file in request")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use PNG, JPG, JPEG, GIF, or WebP.'}), 400
        
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        print(f"✅ Image saved: {unique_filename}")
        
        umkm_data = {
            'owner_id': current_user.id,
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
        
        required_fields = ['name', 'category', 'address', 'phone']
        for field in required_fields:
            if not umkm_data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        new_umkm = UMKM(**umkm_data)
        db.session.add(new_umkm)
        db.session.commit()
        
        print(f"✅ UMKM created successfully: {new_umkm.id}")
        
        base_url = request.host_url.rstrip('/')
        image_url = f"{base_url}api/uploads/images/{new_umkm.image_path}"
        
        umkm_response = {
            'id': new_umkm.id,
            'name': new_umkm.name,
            'category': new_umkm.category,
            'description': new_umkm.description,
            'address': new_umkm.address,
            'contact': new_umkm.phone,
            'image_path': new_umkm.image_path,
            'image_url': image_url,
            'latitude': new_umkm.latitude,
            'longitude': new_umkm.longitude,
            'hours': new_umkm.hours,
            'owner_id': new_umkm.owner_id,
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

# ENDPOINT DELETE UMKM - TAMBAHAN BARU
@umkm_bp.route('/umkm/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_umkm(id):
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        umkm = UMKM.query.get(id)
        if not umkm:
            return jsonify({'error': 'UMKM not found'}), 404
        
        # Cek apakah user adalah pemilik UMKM atau admin
        if umkm.owner_id != current_user.id and current_user.role != 'admin':
            return jsonify({'error': 'You can only delete your own UMKM'}), 403
        
        # Hapus file gambar jika ada
        if umkm.image_path:
            image_path = os.path.join(UPLOAD_FOLDER, umkm.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"✅ Deleted image file: {umkm.image_path}")
        
        # Hapus UMKM dari database
        db.session.delete(umkm)
        db.session.commit()
        
        print(f"✅ UMKM deleted successfully: {id}")
        return jsonify({'message': 'UMKM deleted successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error deleting UMKM {id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@umkm_bp.route('/umkm/<int:id>', methods=['GET', 'OPTIONS'])
def get_umkm_by_id(id):
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        umkm = UMKM.query.get(id)
        if not umkm:
            return jsonify({'error': 'UMKM not found'}), 404
        
        reviews = Review.query.filter_by(umkm_id=id).all()
        avg_rating = 0
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
        
        base_url = request.host_url.rstrip('/')
        image_url = f"{base_url}api/uploads/images/{umkm.image_path}" if umkm.image_path else None
        
        umkm_response = {
            'id': umkm.id,
            'name': umkm.name,
            'category': umkm.category,
            'description': umkm.description,
            'address': umkm.address,
            'contact': umkm.phone,
            'phone': umkm.phone,
            'image_path': umkm.image_path,
            'image_url': image_url,
            'latitude': umkm.latitude,
            'longitude': umkm.longitude,
            'hours': umkm.hours,
            'owner_id': umkm.owner_id,
            'owner_name': umkm.owner.name if umkm.owner else 'Tidak diketahui',
            'avg_rating': round(avg_rating, 1),
            'review_count': len(reviews),
            'created_at': umkm.created_at.isoformat() if umkm.created_at else None
        }
        
        return jsonify(umkm_response)
        
    except Exception as e:
        print(f"❌ Error fetching UMKM {id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@umkm_bp.route('/uploads/images/<filename>', methods=['GET', 'OPTIONS'])
def serve_image(filename):
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(f"❌ Error serving image {filename}: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404

# Endpoint untuk mendapatkan UMKM milik user
@umkm_bp.route('/my-umkm', methods=['GET', 'OPTIONS'])
def get_my_umkm():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        umkms = UMKM.query.filter_by(owner_id=current_user.id).all()
        result = []
        
        for umkm in umkms:
            reviews = Review.query.filter_by(umkm_id=umkm.id).all()
            avg_rating = 0
            if reviews:
                avg_rating = sum(review.rating for review in reviews) / len(reviews)
            
            base_url = request.host_url.rstrip('/')
            image_url = f"{base_url}api/uploads/images/{umkm.image_path}" if umkm.image_path else None
            
            result.append({
                'id': umkm.id,
                'name': umkm.name,
                'description': umkm.description,
                'category': umkm.category,
                'address': umkm.address,
                'contact': umkm.phone,
                'image_url': image_url,
                'image_path': umkm.image_path,
                'avg_rating': round(avg_rating, 1),
                'review_count': len(reviews),
                'created_at': umkm.created_at.isoformat() if umkm.created_at else None
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error fetching user UMKM: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Endpoint untuk reviews (tetap sama)
@umkm_bp.route('/umkm/<int:id>/reviews', methods=['GET', 'POST', 'OPTIONS'])
def handle_reviews(id):
    if request.method == 'OPTIONS':
        return '', 200
    elif request.method == 'GET':
        return get_umkm_reviews(id)
    elif request.method == 'POST':
        return add_umkm_review(id)

def get_umkm_reviews(id):
    try:
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
        
        return jsonify(reviews_data)
        
    except Exception as e:
        print(f"❌ Error fetching reviews for UMKM {id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def add_umkm_review(id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Unauthorized'}), 401
            
        data = request.get_json()
        
        if not data.get('rating') or not data.get('comment'):
            return jsonify({'error': 'Rating and comment are required'}), 400
        
        new_review = Review(
            umkm_id=id,
            user_id=current_user.id,
            rating=data['rating'],
            comment=data['comment']
        )
        
        db.session.add(new_review)
        db.session.commit()
        
        return jsonify({'message': 'Review added successfully'}), 201
        
    except Exception as e:
        print(f"❌ Error adding review for UMKM {id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
