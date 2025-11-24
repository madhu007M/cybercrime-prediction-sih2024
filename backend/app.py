from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import joblib
import os
import datetime

# --- CONFIGURATION ---
app = Flask(__name__)
CORS(app)  # Enables the frontend to talk to this backend

# Paths to your Data & Models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data/crime_data.db')
MODEL_PATH = os.path.join(BASE_DIR, 'data/model_next_loc.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'data/label_encoder.pkl')

# --- LOAD AI MODELS (ONCE AT STARTUP) ---
print("⏳ Loading AI Models...")
try:
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    print("✅ AI Models Loaded Successfully!")
except Exception as e:
    print(f"⚠️ WARNING: Could not load models. Prediction endpoint will fail. Error: {e}")
    model = None
    encoder = None

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name (row['id'])
    return conn

# --- API ENDPOINT 1: HOTSPOTS (For Heatmap) ---
@app.route('/api/hotspots', methods=['GET'])
def get_hotspots():
    """Returns all withdrawal locations to plot the Heatmap."""
    conn = get_db_connection()
    # Get last 500 withdrawals (High risk zones are recent)
    query = "SELECT withdrawal_lat, withdrawal_long, amount FROM complaints ORDER BY timestamp DESC LIMIT 500"
    rows = conn.execute(query).fetchall()
    conn.close()
    
    data = []
    for row in rows:
        data.append({
            "lat": row["withdrawal_lat"],
            "lng": row["withdrawal_long"],
            "weight": row["amount"] / 1000  # Normalize weight for heatmap intensity
        })
    return jsonify(data)

# --- API ENDPOINT 2: MULE HISTORY (For Investigator View) ---
@app.route('/api/mule_history', methods=['GET'])
def get_mule_history():
    """Returns the path taken by a specific criminal."""
    mule_id = request.args.get('mule_id') # e.g., ?mule_id=MULE_RINGLEADER_01
    
    if not mule_id:
        return jsonify({"error": "Please provide a mule_id"}), 400

    conn = get_db_connection()
    query = """
        SELECT withdrawal_lat, withdrawal_long, timestamp, amount, withdrawal_atm_id 
        FROM complaints 
        WHERE mule_account_id = ? 
        ORDER BY timestamp ASC
    """
    rows = conn.execute(query, (mule_id,)).fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "lat": row["withdrawal_lat"],
            "lng": row["withdrawal_long"],
            "time": row["timestamp"],
            "amount": row["amount"],
            "atm": row["withdrawal_atm_id"]
        })
    return jsonify(history)

# --- API ENDPOINT 3: PREDICT NEXT MOVE (The "Magic") ---
@app.route('/api/predict_next', methods=['POST'])
def predict_next():
    """
    Input: JSON { "mule_id": "MULE_01", "current_lat": 28.6, "current_long": 77.2, "hour": 10 }
    Output: JSON { "predicted_lat": 28.65, "predicted_long": 77.25 }
    """
    if not model:
        return jsonify({"error": "Model not loaded"}), 500

    data = request.json
    mule_id = data.get('mule_id')
    current_lat = data.get('current_lat')
    current_long = data.get('current_long')
    
    # Auto-detect current time if not sent
    current_hour = data.get('hour', datetime.datetime.now().hour)
    current_day = datetime.datetime.now().weekday()

    try:
        # 1. Encode the Mule ID (Convert "MULE_01" -> 45)
        # Handle unknown mules safely
        if mule_id in encoder.classes_:
            mule_encoded = encoder.transform([mule_id])[0]
        else:
            # If new mule, assume generic behavior (use ID 0)
            mule_encoded = 0 

        # 2. Prepare Input for AI
        # Must match the order used in training: [mule, lat, long, hour, day]
        features = [[mule_encoded, current_lat, current_long, current_hour, current_day]]
        
        # 3. Predict
        prediction = model.predict(features) # Returns [[lat, long]]
        pred_lat = prediction[0][0]
        pred_long = prediction[0][1]

        return jsonify({
            "predicted_lat": pred_lat,
            "predicted_long": pred_long,
            "confidence": "High",
            "alert_message": f"Suspect likely moving towards Lat: {pred_lat:.4f}, Lng: {pred_long:.4f}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RUN SERVER ---
if __name__ == '__main__':
    # Run on port 5000
    print("🚀 Backend running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)