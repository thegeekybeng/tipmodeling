import sqlite3
import os

def seed_db():
    db_path = "engine/data/phishing.db"
    if not os.path.exists(db_path):
        # If running from root
        db_path = "data/phishing.db"
        
    print(f"Seeding database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    seed_sql_path = "engine/seed_db.sql"
    if not os.path.exists(seed_sql_path):
        seed_sql_path = "seed_db.sql"
        
    with open(seed_sql_path, 'r') as f:
        sql = f.read()
    
    try:
        cur.executescript(sql)
        conn.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_db()
