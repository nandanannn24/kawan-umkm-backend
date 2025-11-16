import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from models import UMKM, db

umkm_bp = Blueprint('umkm', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # Create uploads directory if not exists
        upload_folder = 'uploads/images'
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

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
        
        # Save image
        filename = save_image(file)
        if not filename:
            print("❌ File type not allowed")
            return jsonify({'error': 'File type not allowed. Use PNG, JPG, JPEG, GIF, or WebP.'}), 400
        
        print(f"✅ Image saved: {filename}")
        
        # Get form data - FIXED FIELD NAMES
        umkm_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'address': request.form.get('address'),
            'contact': request.form.get('contact'),  # Changed from 'phone'
            'latitude': request.form.get('latitude', ''),
            'longitude': request.form.get('longitude', ''),
            'image_url': f"/api/uploads/images/{filename}",  # Fixed URL path
        }
        
        # Validate required fields
        required_fields = ['name', 'description', 'category', 'address', 'contact']
        for field in required_fields:
            if not umkm_data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        print("📝 UMKM data to save:", umkm_data)
        
        # Create UMKM
        new_umkm = UMKM(**umkm_data)
        db.session.add(new_umkm)
        db.session.commit()
        
        print(f"✅ UMKM created successfully: {new_umkm.id}")
        
        return jsonify({
            'message': 'UMKM created successfully',
            'umkm': {
                'id': new_umkm.id,
                'name': new_umkm.name,
                'image_url': f"https://kawan-umkm-backend-production.up.railway.app/api/uploads/images/{filename}",
                'description': new_umkm.description,
                'category': new_umkm.category,
                'address': new_umkm.address,
                'contact': new_umkm.contact
            }
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating UMKM: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@umkm_bp.route('/umkm', methods=['GET'])
def get_all_umkm():
    try:
        umkms = UMKM.query.all()
        result = []
        
        for umkm in umkms:
            # Convert to absolute URL for frontend
            image_url = umkm.image_url
            if umkm.image_url and not umkm.image_url.startswith('http'):
                if umkm.image_url.startswith('/api/'):
                    image_url = f"https://kawan-umkm-backend-production.up.railway.app{umkm.image_url}"
                else:
                    image_url = f"https://kawan-umkm-backend-production.up.railway.app/api{umkm.image_url}"
            
            result.append({
                'id': umkm.id,
                'name': umkm.name,
                'description': umkm.description,
                'category': umkm.category,
                'address': umkm.address,
                'contact': umkm.contact,
                'image_url': image_url,
                'latitude': umkm.latitude,
                'longitude': umkm.longitude,
                'created_at': umkm.created_at.isoformat() if umkm.created_at else None
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Error fetching UMKM: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# FIXED: Serve images from correct path
@umkm_bp.route('/uploads/images/<filename>')
def serve_image(filename):
    try:
        return send_from_directory('uploads/images', filename)
    except Exception as e:
        print(f"❌ Error serving image {filename}: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404
