import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models import db, UMKM  # Now this will work

umkm_bp = Blueprint('umkm', __name__)

# Create uploads directory
UPLOAD_FOLDER = 'uploads/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@umkm_bp.route('/umkm', methods=['POST'])
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
        
        # Get form data - FIXED: Get owner_id from authentication
        owner_id = get_jwt_identity() if hasattr(request, 'jwt_identity') else 1
        
        umkm_data = {
            'owner_id': owner_id,
            'name': request.form.get('name'),
            'category': request.form.get('category'),
            'description': request.form.get('description', ''),
            'image_path': unique_filename,
            'latitude': float(request.form.get('latitude')) if request.form.get('latitude') else None,
            'longitude': float(request.form.get('longitude')) if request.form.get('longitude') else None,
            'address': request.form.get('address'),
            'phone': request.form.get('contact'),  # Map 'contact' to 'phone'
            'hours': request.form.get('hours', '09:00-17:00'),  # Default value
            'is_approved': True
        }
        
        # Validate required fields
        required_fields = ['name', 'category', 'address', 'phone']
        for field in required_fields:
            if not umkm_data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        print("📝 UMKM data to save:", umkm_data)
        
        # Create UMKM using SQLAlchemy
        new_umkm = UMKM(**umkm_data)
        db.session.add(new_umkm)
        db.session.commit()
        
        print(f"✅ UMKM created successfully: {new_umkm.id}")
        
        # Build response - FIXED: Use correct field names for frontend
        umkm_response = {
            'id': new_umkm.id,
            'name': new_umkm.name,
            'category': new_umkm.category,
            'description': new_umkm.description,
            'address': new_umkm.address,
            'contact': new_umkm.phone,  # Return as 'contact' for frontend
            'image_path': new_umkm.image_path,  # Keep for compatibility
            'image_url': f"/api/uploads/images/{new_umkm.image_path}",  # Relative path
            'latitude': new_umkm.latitude,
            'longitude': new_umkm.longitude,
            'hours': new_umkm.hours,
            'created_at': new_umkm.created_at.isoformat() if new_umkm.created_at else None,
            'avg_rating': 0,
            'review_count': 0
        }
        
        return jsonify({
            'message': 'UMKM created successfully',
            'umkm': umkm_response
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating UMKM: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
        
@umkm_bp.route('/umkm', methods=['GET'])
def get_all_umkm():
    try:
        umkms = UMKM.query.filter_by(is_approved=True).all()
        result = []
        
        for umkm in umkms:
            result.append({
                'id': umkm.id,
                'name': umkm.name,
                'description': umkm.description,
                'category': umkm.category,
                'address': umkm.address,
                'contact': umkm.phone,  # Return as 'contact'
                'image_url': f"https://kawan-umkm-backend-production.up.railway.app/api/uploads/images/{umkm.image_path}",
                'latitude': umkm.latitude,
                'longitude': umkm.longitude,
                'hours': umkm.hours,
                'created_at': umkm.created_at.isoformat() if umkm.created_at else None
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Error fetching UMKM: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@umkm_bp.route('/uploads/images/<filename>')
def serve_image(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(f"❌ Error serving image {filename}: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404
