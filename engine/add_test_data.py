import sqlite3
import os

def add_multi_node_data():
    db_path = "data/phishing.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Add MYS -> CHN for Industry D26 (Electronics)
        cur.execute("""
            INSERT INTO trade_matrix (source_econ_id, target_econ_id, industry_id, value_added_usd_mn) 
            VALUES ('MYS', 'CHN', 'D26', 12000.0)
            ON CONFLICT (source_econ_id, target_econ_id, industry_id) DO UPDATE 
            SET value_added_usd_mn = EXCLUDED.value_added_usd_mn;
        """)
        conn.commit()
        print("Multi-node test data (MYS -> CHN, D26) added successfully.")
    except Exception as e:
        print(f"Error adding data: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_multi_node_data()
