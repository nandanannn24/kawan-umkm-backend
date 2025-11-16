from flask import Blueprint, request, jsonify
from auth import token_required
from models import db, User, UMKM, Review

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@admin_bp.route('/admin/umkm', methods=['GET'])
@token_required
@admin_required
def get_all_umkm_admin(current_user):
    try:
        # Get all UMKM with owner info and ratings using SQLAlchemy
        umkm_list = UMKM.query.all()
        result = []
        
        for umkm in umkm_list:
            # Get owner info
            owner = User.query.get(umkm.owner_id)
            
            # Calculate average rating and review count
            reviews = Review.query.filter_by(umkm_id=umkm.id).all()
            avg_rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
            review_count = len(reviews)
            
            umkm_data = {
                'id': umkm.id,
                'name': umkm.name,
                'category': umkm.category,
                'description': umkm.description,
                'image_path': umkm.image_path,
                'latitude': umkm.latitude,
                'longitude': umkm.longitude,
                'address': umkm.address,
                'phone': umkm.phone,
                'hours': umkm.hours,
                'is_approved': umkm.is_approved,
                'created_at': umkm.created_at.isoformat() if umkm.created_at else None,
                'owner_name': owner.name if owner else 'Unknown',
                'owner_email': owner.email if owner else 'Unknown',
                'avg_rating': round(avg_rating, 2),
                'review_count': review_count
            }
            result.append(umkm_data)
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error fetching UMKM: {e}")
        return jsonify({'error': 'Failed to fetch UMKM'}), 500

@admin_bp.route('/admin/umkm/<int:umkm_id>/approve', methods=['PUT'])
@token_required
@admin_required
def approve_umkm(current_user, umkm_id):
    try:
        umkm = UMKM.query.get(umkm_id)
        if not umkm:
            return jsonify({'error': 'UMKM not found'}), 404

        umkm.is_approved = True
        db.session.commit()

        return jsonify({'message': 'UMKM approved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error approving UMKM: {e}")
        return jsonify({'error': 'Failed to approve UMKM'}), 500

@admin_bp.route('/admin/stats', methods=['GET'])
@token_required
@admin_required
def get_admin_stats(current_user):
    try:
        total_users = User.query.filter(User.role != 'admin').count()
        total_umkm = UMKM.query.count()
        pending_umkm = UMKM.query.filter_by(is_approved=False).count()
        umkm_owners = db.session.query(UMKM.owner_id).distinct().count()
        
        return jsonify({
            'totalUsers': total_users,
            'totalUMKM': total_umkm,
            'pendingUMKM': pending_umkm,
            'umkmOwners': umkm_owners
        }), 200
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500
