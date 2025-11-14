import os
from app import app, db
from models import User

def setup_production():
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(email='admin@umkm.com').first():
            admin = User(
                username='admin',
                email='admin@umkm.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        print("Production database setup complete!")

if __name__ == '__main__':
    setup_production()