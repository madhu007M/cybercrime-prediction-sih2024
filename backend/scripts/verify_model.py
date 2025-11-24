import pandas as pd
import numpy as np
import sqlite3
import joblib
import os
from math import radians, cos, sin, asin, sqrt

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '../data/crime_data.db')
MODEL_PATH = os.path.join(BASE_DIR, '../data/model_next_loc.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, '../data/label_encoder.pkl')

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 6371 for km
    return c * r * 1000 # Convert to meters

def verify():
    print("⏳ Loading Model and Data...")
    
    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        print("❌ Error: Model file not found. Run train_model.py first.")
        return
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)

    # 2. Load Data (Same logic as training)
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM complaints", conn)
    conn.close()

    # Preprocessing
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['mule_account_id', 'timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['mule_id_encoded'] = encoder.transform(df['mule_account_id'])

    # Create Targets
    df['actual_next_lat'] = df.groupby('mule_account_id')['withdrawal_lat'].shift(-1)
    df['actual_next_long'] = df.groupby('mule_account_id')['withdrawal_long'].shift(-1)
    df = df.dropna(subset=['actual_next_lat', 'actual_next_long'])

    # 3. Run Predictions on ALL data
    X = df[['mule_id_encoded', 'withdrawal_lat', 'withdrawal_long', 'hour', 'day_of_week']]
    
    print(f"🧠 Testing model on {len(df)} past crimes...")
    predictions = model.predict(X)

    # 4. Calculate Error (Distance in Meters)
    distances = []
    for i in range(len(df)):
        act_lat = df.iloc[i]['actual_next_lat']
        act_lng = df.iloc[i]['actual_next_long']
        pred_lat = predictions[i][0]
        pred_lng = predictions[i][1]
        
        dist = haversine(act_lng, act_lat, pred_lng, pred_lat)
        distances.append(dist)

    avg_error = np.mean(distances)
    
    # 5. The Report
    print("\n" + "="*40)
    print("📊 MODEL PERFORMANCE REPORT")
    print("="*40)
    print(f"✅ Total Predictions: {len(df)}")
    print(f"🎯 Average Prediction Error: {avg_error:.2f} meters")
    
    if avg_error < 500:
        print("🌟 STATUS: EXCELLENT (Error < 500m)")
    elif avg_error < 2000:
        print("✅ STATUS: GOOD (Error < 2km)")
    else:
        print("⚠️ STATUS: NEEDS IMPROVEMENT (Error > 2km)")

    # 6. Sanity Check (The Delhi Gang Test)
    print("\n🕵️  SANITY CHECK (Manual Inspection)")
    print("-" * 40)
    # Let's pick 3 random examples to show "Real vs Predicted"
    indices = np.random.choice(df.index, 3, replace=False)
    for idx in indices:
        row = df.loc[idx]
        pred_idx = df.index.get_loc(idx) # Find integer index for prediction array
        pred = predictions[pred_idx]
        
        dist = haversine(row['actual_next_long'], row['actual_next_lat'], pred[1], pred[0])
        
        print(f"📍 From: {row['withdrawal_lat']:.4f}, {row['withdrawal_long']:.4f}")
        print(f"   Expected Next: {row['actual_next_lat']:.4f}, {row['actual_next_long']:.4f}")
        print(f"   AI Predicted:  {pred[0]:.4f}, {pred[1]:.4f}")
        print(f"   Error: {dist:.0f} meters")
        print("-" * 20)

if __name__ == "__main__":
    verify()