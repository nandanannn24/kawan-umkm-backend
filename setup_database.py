import os
from models import create_tables, get_db_connection, hash_password

def setup_database():
    print("🔧 Setting up database...")
    
    if os.path.exists('kawan_umkm.db'):
        os.remove('kawan_umkm.db')
        print("🗑️ Old database removed")

    create_tables()
    
    seed_initial_data()
    
    print("✅ Database setup completed!")

def seed_initial_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        demo_users = [
            ('User Demo', 'user@demo.com', hash_password('password'), 'user'),
            ('UMKM Owner', 'umkm@demo.com', hash_password('password'), 'umkm'),
            ('Admin User', 'admin@demo.com', hash_password('password'), 'admin')
        ]
        
        for user in demo_users:
            cursor.execute(
                'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                user
            )
        cursor.execute('SELECT id FROM users WHERE email = ?', ('umkm@demo.com',))
        umkm_owner_id = cursor.fetchone()[0]
        
        cursor.execute('SELECT id FROM users WHERE email = ?', ('user@demo.com',))
        user_id = cursor.fetchone()[0]
        demo_umkm = [
            (umkm_owner_id, 'Geprek Mbak Rara', 'Makanan', 
             'Ayam geprek dengan sambal mantap dan nasi putih hangat. Bumbu rempah pilihan yang membuat cita rasa semakin nikmat.',
             None, -6.2609, 106.7816, 'Area UPN Veteran Jakarta', '08123456789', '09:00 - 21:00', 1),
            
            (umkm_owner_id, 'Bakso Manjur', 'Makanan',
             'Daging sapi 100% asli, kuah gurih dengan bumbu rahasia keluarga.',
             None, -6.2610, 106.7820, 'Jl. UPN Veteran No. 123', '08123456780', '10:00 - 22:00', 1),
            
            (umkm_owner_id, 'Es Teh Rejeki', 'Minuman',
             'Es teh murni dari pucuk daun asli, segar dan menyegarkan.',
             None, -6.2615, 106.7810, 'Area Kampus UPN', '08123456781', '08:00 - 20:00', 1),
            
            (umkm_owner_id, 'Servis AC', 'Jasa',
             'Segala jenis servis AC awet dan dingin. Teknisi berpengalaman dan terpercaya.',
             None, -6.2620, 106.7800, 'Jl. Veteran No. 45', '08123456782', '24 Jam', 1)
        ]
        
        for umkm in demo_umkm:
            cursor.execute(
                '''INSERT INTO umkm (owner_id, name, category, description, image_path, 
                latitude, longitude, address, phone, hours, is_approved) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                umkm
            )
        cursor.execute('SELECT id FROM umkm WHERE name = ?', ('Geprek Mbak Rara',))
        umkm_id = cursor.fetchone()[0]
        
        demo_reviews = [
            (umkm_id, user_id, 5, 'Enak banget ayam gepreknya, sambalnya pedas mantap!'),
            (umkm_id, user_id, 4, 'Harganya terjangkau, rasanya juga enak. Recommended!')
        ]
        
        for review in demo_reviews:
            cursor.execute(
                'INSERT INTO reviews (umkm_id, user_id, rating, comment) VALUES (?, ?, ?, ?)',
                review
            )
        
        conn.commit()
        print("✅ Demo data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    setup_database()