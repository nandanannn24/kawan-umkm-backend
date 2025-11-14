from flask import Blueprint, request, jsonify
from auth import token_required
from models import get_db_connection

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
            GROUP BY u.id
            ORDER BY u.created_at DESC
        ''')
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

@admin_bp.route('/admin/umkm/<int:umkm_id>/approve', methods=['PUT'])
@token_required
@admin_required
def approve_umkm(current_user, umkm_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE umkm SET is_approved = 1 WHERE id = ?', (umkm_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'UMKM not found'}), 404
            
        return jsonify({'message': 'UMKM approved successfully'}), 200
    finally:
        conn.close()

@admin_bp.route('/admin/stats', methods=['GET'])
@token_required
@admin_required
def get_admin_stats(current_user):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE role != "admin"')
        total_users = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM umkm')
        total_umkm = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM umkm WHERE is_approved = 0')
        pending_umkm = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(DISTINCT owner_id) as count FROM umkm')
        umkm_owners = cursor.fetchone()['count']
        
        return jsonify({
            'totalUsers': total_users,
            'totalUMKM': total_umkm,
            'pendingUMKM': pending_umkm,
            'umkmOwners': umkm_owners
        }), 200
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500
    finally:
        conn.close()