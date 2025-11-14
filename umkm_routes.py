from flask import Blueprint, request, jsonify
from auth import token_required
from config import Config
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from models import get_db_connection
from email_service import send_review_notification_email  # Tambahkan import
from datetime import datetime

umkm_bp = Blueprint('umkm', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        return filename
    return None

@umkm_bp.route('/umkm', methods=['GET'])
def get_all_umkm():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        sort = request.args.get('sort', 'rating')
        
        query = '''
            SELECT u.*, 
                   AVG(r.rating) as avg_rating, 
                   COUNT(r.id) as review_count,
                   us.name as owner_name
            FROM umkm u
            LEFT JOIN reviews r ON u.id = r.umkm_id
            LEFT JOIN users us ON u.owner_id = us.id
            WHERE u.is_approved = 1
        '''
        params = []
        
        if search:
            query += ' AND (u.name LIKE ? OR u.description LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])
        
        if category:
            query += ' AND u.category = ?'
            params.append(category)
        
        query += ' GROUP BY u.id'
        
        if sort == 'rating':
            query += ' ORDER BY avg_rating DESC'
        elif sort == 'reviews':
            query += ' ORDER BY review_count DESC'
        elif sort == 'name':
            query += ' ORDER BY u.name ASC'
        
        cursor.execute(query, params)
        umkm_list = cursor.fetchall()
        
        umkm_list = [dict(row) for row in umkm_list]
        
        for umkm in umkm_list:
            if umkm['avg_rating'] is not None:
                umkm['avg_rating'] = float(umkm['avg_rating'])
            else:
                umkm['avg_rating'] = 0.0
            umkm['review_count'] = umkm['review_count'] or 0
        
        return jsonify(umkm_list), 200
    finally:
        conn.close()

@umkm_bp.route('/umkm/<int:umkm_id>', methods=['GET'])
def get_umkm(umkm_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, 
                   AVG(r.rating) as avg_rating, 
                   COUNT(r.id) as review_count,
                   us.name as owner_name,
                   us.email as owner_email
            FROM umkm u
            LEFT JOIN reviews r ON u.id = r.umkm_id
            LEFT JOIN users us ON u.owner_id = us.id
            WHERE u.id = ? AND u.is_approved = 1
            GROUP BY u.id
        ''', (umkm_id,))
        umkm = cursor.fetchone()
        
        if umkm:
            umkm = dict(umkm)
            if umkm['avg_rating'] is not None:
                umkm['avg_rating'] = float(umkm['avg_rating'])
            else:
                umkm['avg_rating'] = 0.0
            umkm['review_count'] = umkm['review_count'] or 0
            return jsonify(umkm), 200
        else:
            return jsonify({'error': 'UMKM not found'}), 404
    finally:
        conn.close()

@umkm_bp.route('/umkm', methods=['POST'])
@token_required
def create_umkm(current_user):
    if current_user['role'] not in ['umkm', 'admin']:
        return jsonify({'error': 'Only UMKM owners or admin can create UMKM'}), 403

    data = request.form
    name = data.get('name')
    category = data.get('category')
    description = data.get('description')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    address = data.get('address')
    phone = data.get('phone')
    hours = data.get('hours')

    if not name or not category:
        return jsonify({'error': 'Name and category are required'}), 400

    image_file = request.files.get('image')
    image_path = save_image(image_file) if image_file else None

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO umkm (owner_id, name, category, description, image_path, latitude, longitude, address, phone, hours, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (current_user['id'], name, category, description, image_path, latitude, longitude, address, phone, hours))
        umkm_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'message': 'UMKM created successfully', 'id': umkm_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@umkm_bp.route('/umkm/<int:umkm_id>', methods=['PUT'])
@token_required
def update_umkm(current_user, umkm_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT owner_id FROM umkm WHERE id = ?', (umkm_id,))
        umkm = cursor.fetchone()
        if not umkm:
            return jsonify({'error': 'UMKM not found'}), 404
            
        if current_user['role'] != 'admin' and umkm['owner_id'] != current_user['id']:
            return jsonify({'error': 'You can only edit your own UMKM'}), 403

        data = request.form
        name = data.get('name')
        category = data.get('category')
        description = data.get('description')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        address = data.get('address')
        phone = data.get('phone')
        hours = data.get('hours')

        image_file = request.files.get('image')
        image_path = save_image(image_file) if image_file else None

        update_fields = []
        params = []
        
        if name: 
            update_fields.append("name = ?")
            params.append(name)
        if category: 
            update_fields.append("category = ?")
            params.append(category)
        if description is not None: 
            update_fields.append("description = ?")
            params.append(description)
        if latitude: 
            update_fields.append("latitude = ?")
            params.append(latitude)
        if longitude: 
            update_fields.append("longitude = ?")
            params.append(longitude)
        if address: 
            update_fields.append("address = ?")
            params.append(address)
        if phone: 
            update_fields.append("phone = ?")
            params.append(phone)
        if hours: 
            update_fields.append("hours = ?")
            params.append(hours)
        if image_path: 
            update_fields.append("image_path = ?")
            params.append(image_path)
            
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400

        params.append(umkm_id)
        query = f"UPDATE umkm SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        return jsonify({'message': 'UMKM updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@umkm_bp.route('/umkm/<int:umkm_id>/reviews', methods=['GET'])
def get_reviews(umkm_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as user_name
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.umkm_id = ?
            ORDER BY r.created_at DESC
        ''', (umkm_id,))
        reviews = cursor.fetchall()
        reviews = [dict(row) for row in reviews]
        
        return jsonify(reviews), 200
    finally:
        conn.close()

@umkm_bp.route('/umkm/<int:umkm_id>/reviews', methods=['POST'])
@token_required
def create_review(current_user, umkm_id):
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')

    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM umkm WHERE id = ? AND is_approved = 1', (umkm_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'UMKM not found'}), 404
        cursor.execute('SELECT id FROM reviews WHERE umkm_id = ? AND user_id = ?', (umkm_id, current_user['id']))
        if cursor.fetchone():
            return jsonify({'error': 'You have already reviewed this UMKM'}), 400

        cursor.execute('''
            INSERT INTO reviews (umkm_id, user_id, rating, comment)
            VALUES (?, ?, ?, ?)
        ''', (umkm_id, current_user['id'], rating, comment))
        conn.commit()
        
        return jsonify({'message': 'Review added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()