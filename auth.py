from flask import Blueprint, request, jsonify
import jwt
import datetime
from sqlalchemy.exc import IntegrityError
from config import Config
from models import db, User, hash_password, check_password, PasswordResetToken
from email_service import EmailService, create_password_reset_token, verify_password_reset_token, mark_token_used

auth_bp = Blueprint('auth', __name__)

def create_jwt_token(user_id, email, role):
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400

    try:
        hashed_password = hash_password(password)
        
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()

        token = create_jwt_token(new_user.id, new_user.email, new_user.role)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'role': new_user.role
            }
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password(password, user.password):
        token = create_jwt_token(user.id, user.email, user.role)
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logout successful'}), 200

# ENDPOINT FORGOT PASSWORD
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            # Untuk keamanan, tetap return success meskipun email tidak ditemukan
            return jsonify({
                'message': 'If your email is registered, you will receive a password reset link.'
            }), 200

        # Buat token reset password
        token = create_password_reset_token(user.id)
        if not token:
            return jsonify({'error': 'Failed to create reset token'}), 500

        # Kirim email
        email_service = EmailService()
        
        # Gunakan frontend URL yang benar untuk production
        frontend_url = 'https://kawan-umkm-sekawanpapat.netlify.app'
        reset_link = f"{frontend_url}/reset-password?token={token}"
        
        success = email_service.send_password_reset_email(
            user.email, 
            reset_link,
            user.name
        )

        if success:
            print(f"✅ Reset password email sent to {user.email}")
            return jsonify({
                'message': 'If your email is registered, you will receive a password reset link.'
            }), 200
        else:
            return jsonify({'error': 'Failed to send reset email. Please try again.'}), 500

    except Exception as e:
        print(f"❌ Error in forgot-password: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ENDPOINT RESET PASSWORD
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('newPassword')

        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400

        # Verifikasi token
        user_id = verify_password_reset_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update password
        hashed_password = hash_password(new_password)
        user.password = hashed_password
        db.session.commit()

        # Tandai token sebagai sudah digunakan
        mark_token_used(token)

        return jsonify({'message': 'Password reset successfully'}), 200

    except Exception as e:
        print(f"❌ Error in reset-password: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# ENDPOINT VERIFY TOKEN
@auth_bp.route('/check-token/<token>', methods=['GET'])
def check_token(token):
    try:
        user_id = verify_password_reset_token(token)
        if user_id:
            return jsonify({'valid': True, 'user_id': user_id}), 200
        else:
            return jsonify({'valid': False}), 400
    except Exception as e:
        print(f"❌ Error verifying token: {str(e)}")
        return jsonify({'valid': False}), 400

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = {
                'id': data['user_id'],
                'email': data['email'],
                'role': data['role']
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
