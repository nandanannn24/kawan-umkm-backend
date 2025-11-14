import os
from models import create_tables, get_db_connection

def reset_database():
    # Hapus database lama jika ada
    if os.path.exists('kawan_umkm.db'):
        os.remove('kawan_umkm.db')
        print("🗑️  Old database deleted")
    
    # Buat tabel baru
    create_tables()
    print("✅ New database created with correct structure")

if __name__ == "__main__":
    reset_database()