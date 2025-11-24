import sqlite3
import pandas as pd
import random
import os
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker('en_IN')
Faker.seed(42)

def get_database_path():
    """
    Dynamically finds the 'backend' folder and creates a 'data' folder inside it.
    This ensures the DB is saved in 'backend/data/' regardless of where you run the script.
    """
    # Get the directory where THIS script (generate_data.py) is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go one level up to 'backend', then into 'data'
    # path: .../backend/scripts/../data/crime_data.db
    data_dir = os.path.join(script_dir, '..', 'data')
    
    # Create the folder if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Return the full path to the database file
    return os.path.join(data_dir, 'crime_data.db')

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"✅ Connected to SQLite at: {db_file}")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
    return conn

def create_table(conn):
    sql_create_table = """
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        fraud_type TEXT NOT NULL,
        amount INTEGER,
        mule_account_id TEXT,
        withdrawal_atm_id TEXT,
        withdrawal_lat REAL,
        withdrawal_long REAL,
        location_name TEXT,
        timestamp DATETIME,
        status TEXT
    );
    """
    try:
        c = conn.cursor()
        c.execute(sql_create_table)
        print("✅ Table 'complaints' created.")
    except Exception as e:
        print(e)

def generate_data(conn, num_rows=2000):
    data = []
    
    # --- PATTERN 1: The Delhi ATM Gang (For Prediction Demo) ---
    delhi_atms = [
        {"id": "ATM_DEL_01", "lat": 28.6315, "long": 77.2167, "loc": "Connaught Place Block A"},
        {"id": "ATM_DEL_02", "lat": 28.6290, "long": 77.2190, "loc": "Connaught Place Block B"},
        {"id": "ATM_DEL_03", "lat": 28.6320, "long": 77.2200, "loc": "Barakhamba Road"}
    ]
    delhi_mules = ['MULE_RINGLEADER_01', 'MULE_RINGLEADER_02']

    # --- PATTERN 2: The Bangalore Phishing Ring (For Heatmap Demo) ---
    blr_lat_base = 12.9716
    blr_long_base = 77.5946
    
    print("⏳ Generating synthetic data...")

    for i in range(num_rows):
        # 20% Delhi Gang (Prediction Pattern)
        if random.random() < 0.20:
            mule_id = random.choice(delhi_mules)
            atm = random.choice(delhi_atms)
            lat = atm["lat"] + random.uniform(-0.0005, 0.0005)
            lng = atm["long"] + random.uniform(-0.0005, 0.0005)
            loc_name = atm["loc"]
            atm_id = atm["id"]
            fraud = "Investment Scam"
            amt = random.randint(50000, 500000)
        
        # 30% Bangalore Cluster (Heatmap Pattern)
        elif random.random() < 0.30:
            mule_id = f"MULE_BLR_{random.randint(100, 999)}"
            lat = blr_lat_base + random.uniform(-0.02, 0.02)
            lng = blr_long_base + random.uniform(-0.02, 0.02)
            loc_name = "Bangalore Urban"
            atm_id = f"ATM_BLR_{random.randint(1000,9999)}"
            fraud = "UPI Phishing"
            amt = random.randint(2000, 20000)
            
        # 50% Random Noise
        else:
            mule_id = f"MULE_RAND_{random.randint(1000, 9999)}"
            loc = fake.local_latlng(country_code='IN')
            lat = float(loc[0])
            lng = float(loc[1])
            loc_name = f"{loc[2]}, India"
            atm_id = f"ATM_GEN_{random.randint(10000,99999)}"
            fraud = random.choice(["Job Scam", "Lottery Fraud", "Matrimonial Scam"])
            amt = random.randint(1000, 100000)

        event_time = fake.date_time_this_year()
        
        row = (
            f"CMP{10000+i}", fraud, amt, mule_id, atm_id, 
            lat, lng, loc_name, event_time, "Open"
        )
        data.append(row)

    sql_insert = """
    INSERT INTO complaints (complaint_id, fraud_type, amount, mule_account_id, withdrawal_atm_id, withdrawal_lat, withdrawal_long, location_name, timestamp, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    c = conn.cursor()
    c.executemany(sql_insert, data)
    conn.commit()
    print(f"✅ Successfully inserted {num_rows} rows.")

if __name__ == "__main__":
    # 1. Get correct path (backend/data/crime_data.db)
    db_path = get_database_path()
    
    # 2. Connect
    conn = create_connection(db_path)
    
    if conn is not None:
        # 3. Create Table & Generate Data
        create_table(conn)
        generate_data(conn)
        
        # 4. Optional: Save CSV backup in the same folder
        csv_path = db_path.replace('.db', '.csv')
        db_df = pd.read_sql_query("SELECT * FROM complaints", conn)
        db_df.to_csv(csv_path, index=False)
        print(f"✅ Backup CSV created at: {csv_path}")
        
        conn.close()
    else:
        print("Error! Cannot create the database connection.")