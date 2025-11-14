from flask import Blueprint, request, jsonify
from auth import token_required
from models import get_db_connection, hash_password, check_password
from email_service import create_password_reset_token, verify_password_reset_token, mark_token_used, EmailService
from datetime import datetime
import os

user_bp = Blueprint('user', __name__)

# Check if email service is available
EMAIL_SERVICE_AVAILABLE = os.getenv('EMAIL_USER') and os.getenv('EMAIL_PASSWORD')

def format_join_date(created_at):
    """Format created_at to Indonesian date format"""
    if isinstance(created_at, str):
        try:
            dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                dt = datetime.strptime(created_at, '%Y-%m-%d')
            except ValueError:
                return '2024'
    else:
        dt = created_at
    
    # Format to Indonesian: "14 Januari 2025, 15:30 WIB"
    month_names = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    month = month_names[dt.month - 1]
    return f"{dt.day} {month} {dt.year}, {dt.hour:02d}:{dt.minute:02d} WIB"

@user_bp.route('/user/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):  # ⚠️ UBAH NAMA FUNCTION
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, email, role, created_at FROM users WHERE id = ?', 
            (current_user['id'],)
        )
        user = cursor.fetchone()
        
        if user:
            user_dict = dict(user)
            # Format join date
            if user_dict['created_at']:
                join_date = format_join_date(user_dict['created_at'])
                user_dict['joined_date'] = join_date
            else:
                user_dict['joined_date'] = '2024'
                
            # Get user stats
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT f.umkm_id) as favorite_count,
                    COUNT(DISTINCT r.id) as review_count
                FROM users u
                LEFT JOIN favorites f ON u.id = f.user_id
                LEFT JOIN reviews r ON u.id = r.user_id
                WHERE u.id = ?
            ''', (current_user['id'],))
            
            stats = cursor.fetchone()
            user_dict['favorite_count'] = stats['favorite_count'] or 0
            user_dict['review_count'] = stats['review_count'] or 0
            user_dict['rating_count'] = stats['review_count'] or 0  # Same as review_count
            
            return jsonify(user_dict), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_user_profile(current_user):  # ⚠️ UBAH NAMA FUNCTION
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()

    if not name:
        return jsonify({'error': 'Name is required'}), 400
        
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if email already exists for other users
        cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, current_user['id']))
        if cursor.fetchone():
            return jsonify({'error': 'Email sudah digunakan'}), 400

        # Update user profile
        cursor.execute('''
            UPDATE users 
            SET name = ?, email = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (name, email, current_user['id']))
        
        conn.commit()
        
        # Get updated user data
        cursor.execute('''
            SELECT id, name, email, role, created_at 
            FROM users WHERE id = ?
        ''', (current_user['id'],))
        updated_user = cursor.fetchone()
        
        if not updated_user:
            return jsonify({'error': 'User not found after update'}), 404
        
        # Get updated stats
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT f.umkm_id) as favorite_count,
                COUNT(DISTINCT r.id) as review_count
            FROM users u
            LEFT JOIN favorites f ON u.id = f.user_id
            LEFT JOIN reviews r ON u.id = r.user_id
            WHERE u.id = ?
        ''', (current_user['id'],))
        
        stats = cursor.fetchone()
        
        user_response = dict(updated_user)
        user_response['favorite_count'] = stats['favorite_count'] or 0
        user_response['review_count'] = stats['review_count'] or 0
        user_response['rating_count'] = stats['review_count'] or 0
        
        # Format join date
        if updated_user['created_at']:
            join_date = format_join_date(updated_user['created_at'])
            user_response['joined_date'] = join_date
        else:
            user_response['joined_date'] = '2024'
        
        return jsonify({
            'message': 'Profil berhasil diupdate',
            'user': user_response
        }), 200
        
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    finally:
        conn.close()

@user_bp.route('/change-password', methods=['POST'])
@token_required
def change_user_password(current_user):  # ⚠️ UBAH NAMA FUNCTION
    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')

    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get current password
        cursor.execute('SELECT password FROM users WHERE id = ?', (current_user['id'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Verify current password
        if not check_password(current_password, user['password']):
            return jsonify({'error': 'Password saat ini salah'}), 400

        # Hash new password
        hashed_password = hash_password(new_password)
        
        # Update password
        cursor.execute('''
            UPDATE users 
            SET password = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (hashed_password, current_user['id']))
        
        conn.commit()
        
        return jsonify({'message': 'Password berhasil diubah'}), 200
        
    except Exception as e:
        print(f"❌ Error changing password: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()

@user_bp.route('/forgot-password', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, name, email FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            # Return success even if user doesn't exist for security
            return jsonify({'message': 'Jika email terdaftar, link reset telah dikirim'}), 200

        # Create reset token
        token = create_password_reset_token(user['id'])
        if not token:
            return jsonify({'error': 'Gagal membuat token reset'}), 500

        # Send email
        email_service = EmailService()
        email_sent = email_service.send_password_reset_email(user['email'], token, user['name'])
        
        if email_sent:
            return jsonify({'message': 'Email reset password telah dikirim'}), 200
        else:
            # Fallback for development - return token directly
            reset_link = f"http://localhost:3000/reset-password?token={token}"
            return jsonify({
                'message': 'Email service unavailable. Use this reset link:',
                'reset_link': reset_link,
                'token': token  # For development only
            }), 200

    except Exception as e:
        print(f"❌ Error in forgot password: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()

@user_bp.route('/reset-password', methods=['POST'])
def reset_password():  # ⚠️ UBAH NAMA FUNCTION (HAPUS _with_token)
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('newPassword')

    if not token or not new_password:
        return jsonify({'error': 'Token dan password baru diperlukan'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'Password baru minimal 6 karakter'}), 400

    # Verify token
    user_id = verify_password_reset_token(token)
    if not user_id:
        return jsonify({'error': 'Token tidak valid atau sudah kadaluarsa'}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Hash new password
        hashed_password = hash_password(new_password)
        
        # Update password
        cursor.execute('''
            UPDATE users 
            SET password = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (hashed_password, user_id))
        
        # Mark token as used
        mark_token_used(token)
        
        conn.commit()
        
        return jsonify({
            'message': 'Password berhasil direset',
            'success': True
        }), 200
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return jsonify({'error': 'Terjadi kesalahan internal server'}), 500
    finally:
        conn.close()

@user_bp.route('/check-token/<token>', methods=['GET'])
def verify_reset_token(token):
    """Check if reset token is valid"""
    user_id = verify_password_reset_token(token)
    if user_id:
        return jsonify({'valid': True, 'message': 'Token valid'}), 200
    else:
        return jsonify({'valid': False, 'error': 'Token tidak valid atau kadaluarsa'}), 400