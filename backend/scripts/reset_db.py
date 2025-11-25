import sqlite3
import os

# Get the correct path to the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '../data/crime_data.db')

def reset_status():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Set ALL accounts back to 'Open' (Active)
    cursor.execute("UPDATE complaints SET status = 'Open'")
    conn.commit()
    
    print(f"✅ Database Reset: All accounts are now ACTIVE again.")
    print(f"   Rows updated: {cursor.rowcount}")
    
    conn.close()

if __name__ == "__main__":
    reset_status()