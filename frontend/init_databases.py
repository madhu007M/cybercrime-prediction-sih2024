"""
Initialize all databases for I4C Cybercrime Analytics Portal
Creates: complaints.db, predictions.db, alerts.db with sample data
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

def init_complaints_db():
    """Create complaints database with realistic cybercrime data"""
    db_path = os.path.join(os.path.dirname(__file__), 'complaints.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create complaints table
    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE NOT NULL,
            victim_name TEXT NOT NULL,
            victim_phone TEXT,
            victim_email TEXT,
            fraud_type TEXT NOT NULL,
            amount_lost REAL NOT NULL,
            mule_account TEXT,
            mule_bank TEXT,
            complaint_date TIMESTAMP NOT NULL,
            incident_date TIMESTAMP,
            incident_location TEXT,
            incident_city TEXT NOT NULL,
            incident_state TEXT NOT NULL,
            status TEXT DEFAULT 'Under Investigation',
            priority TEXT DEFAULT 'Medium',
            assigned_to TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sample data for impressive demo
    fraud_types = [
        'UPI Fraud', 'Credit Card Fraud', 'Investment Scam', 
        'Job Fraud', 'Lottery Scam', 'Online Shopping Fraud',
        'Phishing', 'Romance Scam', 'Loan Fraud', 'Cyber Extortion'
    ]
    
    cities = ['Bangalore', 'Delhi', 'Mumbai', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata']
    states = ['Karnataka', 'Delhi', 'Maharashtra', 'Tamil Nadu', 'Telangana', 'Maharashtra', 'West Bengal']
    banks = ['SBI', 'HDFC', 'ICICI', 'Axis', 'PNB', 'Kotak', 'Yes Bank', 'Canara Bank']
    statuses = ['Under Investigation', 'Evidence Collected', 'Account Frozen', 'Resolved', 'Pending']
    priorities = ['Low', 'Medium', 'High', 'Critical']
    
    # Generate 50 sample complaints
    for i in range(1, 51):
        complaint_id = f"CC-2024-{10000 + i}"
        victim_name = f"Victim_{i}"
        fraud_type = random.choice(fraud_types)
        amount = round(random.uniform(5000, 500000), 2)
        mule_account = f"{random.randint(1000000000, 9999999999)}"
        mule_bank = random.choice(banks)
        city_idx = random.randint(0, len(cities)-1)
        city = cities[city_idx]
        state = states[city_idx]
        status = random.choice(statuses)
        priority = random.choice(priorities)
        complaint_date = datetime.now() - timedelta(days=random.randint(0, 30))
        incident_date = complaint_date - timedelta(days=random.randint(0, 5))

        c.execute('''
            INSERT INTO complaints (
                complaint_id, victim_name, victim_phone, fraud_type, 
                amount_lost, mule_account, mule_bank, complaint_date, 
                incident_date, incident_city, incident_state, 
                status, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            complaint_id, victim_name, f"+91-{random.randint(7000000000, 9999999999)}", 
            fraud_type, amount, mule_account, mule_bank, complaint_date, 
            incident_date, city, state, status, priority
        ))
    
    conn.commit()
    conn.close()
    print("✅ Complaints database created with 50 sample records")

def init_predictions_db():
    """Create predictions database with ML prediction results"""
    db_path = os.path.join(os.path.dirname(__file__), 'predictions.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create predictions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id TEXT UNIQUE NOT NULL,
            complaint_id TEXT NOT NULL,
            mule_account TEXT,
            prediction_method TEXT NOT NULL,
            predicted_atm_1 TEXT NOT NULL,
            predicted_city_1 TEXT NOT NULL,
            confidence_1 REAL NOT NULL,
            predicted_atm_2 TEXT,
            predicted_city_2 TEXT,
            confidence_2 REAL,
            predicted_atm_3 TEXT,
            predicted_city_3 TEXT,
            confidence_3 REAL,
            prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Active',
            actual_withdrawal_atm TEXT,
            prediction_accurate INTEGER DEFAULT 0,
            notes TEXT
        )
    ''')
    
    # Sample prediction data
    atm_locations_bangalore = [
        'Koramangala ATM-01', 'MG Road ATM-05', 'Indiranagar ATM-03',
        'Whitefield ATM-02', 'Electronic City ATM-04', 'Marathahalli ATM-06'
    ]
    
    atm_locations_delhi = [
        'Connaught Place ATM-01', 'Karol Bagh ATM-03', 'Dwarka ATM-02',
        'Saket ATM-05', 'Rohini ATM-04', 'Lajpat Nagar ATM-06'
    ]
    
    methods = ['AI/ML Model', 'Transaction Pattern', 'Hybrid Analysis']
    
    # Generate 20 predictions
    for i in range(1, 21):
        pred_id = f"PRED-2024-{5000 + i}"
        complaint_id = f"CC-2024-{10000 + random.randint(1, 50)}"
        mule_account = f"{random.randint(1000000000, 9999999999)}"
        method = random.choice(methods)
        
        # Choose city
        city = random.choice(['Bangalore', 'Delhi'])
        atms = atm_locations_bangalore if city == 'Bangalore' else atm_locations_delhi
        
        # Top 3 predictions with decreasing confidence
        conf1 = round(random.uniform(75, 95), 2)
        conf2 = round(conf1 - random.uniform(5, 15), 2)
        conf3 = round(conf2 - random.uniform(5, 15), 2)
        
        atm_sample = random.sample(atms, 3)
        
        # Random accuracy for some predictions
        accurate = random.choice([0, 0, 1])  # 33% accurate
        
        try:
            c.execute('''
                INSERT INTO predictions (
                    prediction_id, complaint_id, mule_account, prediction_method,
                    predicted_atm_1, predicted_city_1, confidence_1,
                    predicted_atm_2, predicted_city_2, confidence_2,
                    predicted_atm_3, predicted_city_3, confidence_3,
                    prediction_accurate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pred_id, complaint_id, mule_account, method,
                atm_sample[0], city, conf1,
                atm_sample[1], city, conf2,
                atm_sample[2], city, conf3,
                accurate
            ))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print("✅ Predictions database created with 20 sample records")

def init_alerts_db():
    """Create alerts database for real-time notifications"""
    db_path = os.path.join(os.path.dirname(__file__), 'alerts.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create alerts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id TEXT UNIQUE NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            complaint_id TEXT,
            prediction_id TEXT,
            location TEXT,
            action_required TEXT,
            assigned_to TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged_at TIMESTAMP,
            resolved_at TIMESTAMP
        )
    ''')
    
    # Sample alerts
    alert_types = [
        'High Confidence Prediction', 'Suspicious Transaction', 
        'ATM Surveillance Required', 'Account Frozen', 
        'Withdrawal Detected', 'Pattern Match Found'
    ]
    
    severities = ['Low', 'Medium', 'High', 'Critical']
    
    locations = [
        'Koramangala, Bangalore', 'Connaught Place, Delhi', 
        'MG Road, Bangalore', 'Karol Bagh, Delhi',
        'Indiranagar, Bangalore', 'Dwarka, Delhi'
    ]
    
    # Generate 15 alerts
    for i in range(1, 16):
        alert_id = f"ALERT-2024-{3000 + i}"
        alert_type = random.choice(alert_types)
        severity = random.choice(severities)
        location = random.choice(locations)
        
        hours_ago = random.randint(0, 48)
        created_at = datetime.now() - timedelta(hours=hours_ago)
        
        title = f"{alert_type} - {location}"
        message = f"System detected {alert_type.lower()} at {location}. Immediate attention required."
        
        status = random.choice(['Active', 'Active', 'Acknowledged', 'Resolved'])
        
        try:
            c.execute('''
                INSERT INTO alerts (
                    alert_id, alert_type, severity, title, message,
                    location, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert_id, alert_type, severity, title, message,
                location, status, created_at
            ))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print("✅ Alerts database created with 15 sample records")

def init_users_db():
    """Create users database for system users"""
    db_path = os.path.join(os.path.dirname(__file__), 'users.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT
        )
    ''')
    
    # Sample users
    users = [
        ("admin@i4c.gov.in", "Admin@123", "I4C Officer", "All India"),
        ("bank1@bank.com", "Bank@123", "Bank Official", "HDFC Bank"),
        ("bank2@bank.com", "Bank@123", "Bank Official", "SBI Bank"),
        ("police_ka@tnpolice.gov.in", "Police@123", "State Police", "Tamil Nadu"),
        ("police_ka@delhipolice.gov.in", "Police@123", "State Police", "Delhi"),
        ("cbi@cbi.gov.in", "CBI@123", "Central Police", "CBI"),
        ("cybercell@maharashtra.gov.in", "Cyber@123", "Law Enforcement Agency", "Maharashtra"),
    ]
    
    # Insert users into the database
    for email, password, role, department in users:
        try:
            c.execute('''
                INSERT INTO users (email, password, role, department) 
                VALUES (?, ?, ?, ?)
            ''', (email, password, role, department))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print("✅ Users database created with sample user records")

def main():
    """Initialize all databases"""
    print("\n🔄 Initializing I4C Cybercrime Databases...\n")
    
    init_complaints_db()
    init_predictions_db()
    init_alerts_db()
    init_users_db()
    
    print("\n✅ ALL DATABASES INITIALIZED SUCCESSFULLY!\n")
    print("Created databases:")
    print("  📁 complaints.db  - 50 cybercrime complaints")
    print("  📁 predictions.db - 20 ML predictions")
    print("  📁 alerts.db      - 15 real-time alerts")
    print("  📁 users.db       - sample user records")
    print("\n🚀 Ready for hackathon demo!\n")

if __name__ == "__main__":
    main()