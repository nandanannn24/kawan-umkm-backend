import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import UMKM, db

umkm_bp = Blueprint('umkm', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file):
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # Ensure upload directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

@umkm_bp.route('/umkm', methods=['POST'])
def create_umkm():
    try:
        print("📥 Received UMKM creation request")
        
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
            return jsonify({'error': 'File type not allowed'}), 400
        
        print(f"✅ Image saved: {filename}")
        
        # Get form data
        umkm_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'address': request.form.get('address'),
            'contact': request.form.get('contact'),
            'latitude': request.form.get('latitude'),
            'longitude': request.form.get('longitude'),
            'image_url': f"/uploads/images/{filename}",  # Relative path
            'user_id': request.form.get('user_id')  # Assuming you have user auth
        }
        
        # Validate required fields
        required_fields = ['name', 'description', 'category', 'address', 'contact']
        for field in required_fields:
            if not umkm_data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
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
                'image_url': f"https://kawan-umkm-backend-production.up.railway.app/uploads/images/{filename}",
                # ... other fields
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
                image_url = f"https://kawan-umkm-backend-production.up.railway.app{umkm.image_url}"
            
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

@umkm_bp.route('/uploads/images/<filename>')
def serve_image(filename):
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"❌ Error serving image {filename}: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404
