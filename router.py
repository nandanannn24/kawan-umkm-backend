from flask import request, jsonify
from models import UMKM, Review

def register_routes(app):
    
    @app.route('/api/umkm', methods=['GET', 'POST', 'OPTIONS'])
    def handle_umkm():
        if request.method == 'OPTIONS':
            return '', 200
        elif request.method == 'GET':
            return get_all_umkm()
        elif request.method == 'POST':
            # Anda bisa memindahkan logika create_umkm ke sini
            return jsonify({'message': 'Create UMKM endpoint'}), 201

    def get_all_umkm():
        try:
            print("📥 [ROUTES] Fetching all UMKM...")
            umkms = UMKM.query.filter_by(is_approved=True).all()
            result = []
            
            for umkm in umkms:
                reviews = Review.query.filter_by(umkm_id=umkm.id).all()
                avg_rating = 0
                if reviews:
                    avg_rating = sum(review.rating for review in reviews) / len(reviews)
                
                result.append({
                    'id': umkm.id,
                    'name': umkm.name,
                    'description': umkm.description,
                    'category': umkm.category,
                    'address': umkm.address,
                    'contact': umkm.phone,
                    'image_url': f"https://kawan-umkm-backend-production.up.railway.app/api/uploads/images/{umkm.image_path}",
                    'image_path': umkm.image_path,
                    'latitude': umkm.latitude,
                    'longitude': umkm.longitude,
                    'hours': umkm.hours,
                    'avg_rating': round(avg_rating, 1),
                    'review_count': len(reviews),
                    'created_at': umkm.created_at.isoformat() if umkm.created_at else None
                })
            
            print(f"✅ [ROUTES] Found {len(result)} UMKM")
            return jsonify(result)
        
        except Exception as e:
            print(f"❌ [ROUTES] Error fetching UMKM: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/umkm/<int:id>', methods=['GET', 'OPTIONS'])
    def get_umkm_by_id(id):
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            print(f"🔍 [ROUTES] Fetching UMKM with ID: {id}")
            
            umkm = UMKM.query.get(id)
            if not umkm:
                return jsonify({'error': 'UMKM not found'}), 404
            
            reviews = Review.query.filter_by(umkm_id=id).all()
            avg_rating = 0
            if reviews:
                avg_rating = sum(review.rating for review in reviews) / len(reviews)
            
            umkm_response = {
                'id': umkm.id,
                'name': umkm.name,
                'category': umkm.category,
                'description': umkm.description,
                'address': umkm.address,
                'contact': umkm.phone,
                'image_url': f"https://kawan-umkm-backend-production.up.railway.app/api/uploads/images/{umkm.image_path}",
                'latitude': umkm.latitude,
                'longitude': umkm.longitude,
                'hours': umkm.hours,
                'avg_rating': round(avg_rating, 1),
                'review_count': len(reviews),
                'created_at': umkm.created_at.isoformat() if umkm.created_at else None
            }
            
            return jsonify(umkm_response)
            
        except Exception as e:
            print(f"❌ [ROUTES] Error fetching UMKM {id}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
