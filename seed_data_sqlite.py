from models import get_db_connection, hash_password

def seed_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM favorites')
        cursor.execute('DELETE FROM reviews')
        cursor.execute('DELETE FROM umkm')
        cursor.execute('DELETE FROM users')
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
        
        conn.commit()
        print("✅ Demo users seeded successfully! (No UMKM data)")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    seed_data()