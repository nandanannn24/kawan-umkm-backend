from flask import Blueprint, request, jsonify
import jwt
import datetime
from sqlalchemy.exc import IntegrityError
from config import Config
from models import db, User, hash_password, check_password  # SQLAlchemy models

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

    # Check if user already exists using SQLAlchemy
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400

    try:
        hashed_password = hash_password(password)
        
        # Create new user with SQLAlchemy
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

    # Find user using SQLAlchemy
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
