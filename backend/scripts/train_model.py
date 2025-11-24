import pandas as pd
import numpy as np
import sqlite3
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# --- CONFIG ---
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/crime_data.db')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../data/model_next_loc.pkl')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), '../data/label_encoder.pkl')

def train():
    print("⏳ Loading data from Database...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM complaints", conn)
    conn.close()

    # 1. PREPROCESSING
    # Convert timestamp to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by Mule ID and Time (Crucial for "Next Location" logic)
    df = df.sort_values(by=['mule_account_id', 'timestamp'])

    # Create Features: Hour of day, Day of week
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek

    # Encode Mule IDs (AI cannot read strings like "MULE_01")
    le = LabelEncoder()
    df['mule_id_encoded'] = le.fit_transform(df['mule_account_id'])

    # 2. CREATE TARGETS (The "Next Location" Logic)
    # We shift the lat/long columns up by 1 row to see the "Future"
    df['next_lat'] = df.groupby('mule_account_id')['withdrawal_lat'].shift(-1)
    df['next_long'] = df.groupby('mule_account_id')['withdrawal_long'].shift(-1)

    # Drop the last row of every mule (because it has no "next" location)
    df = df.dropna(subset=['next_lat', 'next_long'])

    # 3. DEFINE INPUTS (X) AND OUTPUTS (Y)
    features = ['mule_id_encoded', 'withdrawal_lat', 'withdrawal_long', 'hour', 'day_of_week']
    targets = ['next_lat', 'next_long']

    X = df[features]
    y = df[targets]

    # 4. TRAIN MODEL
    print(f"🧠 Training Random Forest on {len(df)} patterns...")
    # n_estimators=100 means we use 100 "Decision Trees" voting together
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # 5. SAVE EVERYTHING
    joblib.dump(model, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH) # Save the name translator too
    
    print("✅ Model Trained & Saved Successfully!")
    print(f"📂 Saved to: {MODEL_PATH}")

    # --- TEST THE MODEL (Optional) ---
    sample_input = X.iloc[0:1] # Take the first real row
    prediction = model.predict(sample_input)
    print(f"\n🔍 TEST PREDICTION:")
    print(f"   Input Location: {X.iloc[0]['withdrawal_lat']}, {X.iloc[0]['withdrawal_long']}")
    print(f"   Predicted Next: {prediction[0][0]}, {prediction[0][1]}")
    print(f"   Actual Next:    {y.iloc[0]['next_lat']}, {y.iloc[0]['next_long']}")

if __name__ == "__main__":
    train()