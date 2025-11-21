from flask import Blueprint, request, jsonify
from auth import token_required
from models import db, User, Favorite, Review, hash_password, check_password
from datetime import datetime
import os
import traceback

user_bp = Blueprint('user', __name__)

def format_join_date(created_at):
    """Format created_at to Indonesian date format"""
    try:
        if created_at:
            # Handle both string and datetime objects
            if isinstance(created_at, str):
                # Remove timezone info if present
                if 'Z' in created_at:
                    created_at = created_at.replace('Z', '+00:00')
                created_at = datetime.fromisoformat(created_at)
            
            month_names = [
                'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
            ]
            month = month_names[created_at.month - 1]
            return f"{created_at.day} {month} {created_at.year}"
        else:
            return "Tidak diketahui"
    except Exception as e:
        print(f"❌ Error formatting date: {e}")
        return "Tidak diketahui"

@user_bp.route('/user/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    try:
        print(f"🔍 Fetching profile for user ID: {current_user['id']}")
        
        user = User.query.get(current_user['id'])
        if not user:
            print(f"❌ User not found for ID: {current_user['id']}")
            return jsonify({'error': 'User not found'}), 404

        # Get stats menggunakan try-except untuk setiap query
        try:
            favorite_count = Favorite.query.filter_by(user_id=current_user['id']).count()
        except Exception as e:
            print(f"❌ Error counting favorites: {e}")
            favorite_count = 0

        try:
            review_count = Review.query.filter_by(user_id=current_user['id']).count()
        except Exception as e:
            print(f"❌ Error counting reviews: {e}")
            review_count = 0

        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'joined_date': format_join_date(user.created_at),
            'favorite_count': favorite_count,
            'review_count': review_count,
            'rating_count': review_count,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }

        print(f"✅ Profile data retrieved for: {user.email}")
        return jsonify(user_data), 200

    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        print(f"🔍 Stack trace: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_user_profile(current_user):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()

        if not name:
            return jsonify({'error': 'Name is required'}), 400
            
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.get(current_user['id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check if email already exists for other users
        existing_user = User.query.filter(
            User.email == email, 
            User.id != current_user['id']
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Email sudah digunakan'}), 400

        # Update user
        user.name = name
        user.email = email
        db.session.commit()

        # Get updated stats
        try:
            favorite_count = Favorite.query.filter_by(user_id=current_user['id']).count()
        except:
            favorite_count = 0
            
        try:
            review_count = Review.query.filter_by(user_id=current_user['id']).count()
        except:
            review_count = 0

        user_response = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'joined_date': format_join_date(user.created_at),
            'favorite_count': favorite_count,
            'review_count': review_count,
            'rating_count': review_count,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }

        return jsonify({
            'message': 'Profil berhasil diupdate',
            'user': user_response
        }), 200
        
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        print(f"🔍 Stack trace: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@user_bp.route('/change-password', methods=['POST'])
@token_required
def change_user_password(current_user):
    try:
        data = request.get_json()
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')

        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400

        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400

        user = User.query.get(current_user['id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Verify current password
        if not check_password(current_password, user.password):
            return jsonify({'error': 'Password saat ini salah'}), 400

        # Hash and update new password
        hashed_password = hash_password(new_password)
        user.password = hashed_password
        db.session.commit()

        return jsonify({'message': 'Password berhasil diubah'}), 200
        
    except Exception as e:
        print(f"❌ Error changing password: {e}")
        print(f"🔍 Stack trace: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
