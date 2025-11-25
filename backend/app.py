from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import joblib
import os
import datetime
from twilio.rest import Client
from dotenv import load_dotenv


load_dotenv()
# --- CONFIGURATION ---
app = Flask(__name__)
CORS(app)  # Enables the frontend to talk to this backend

# --- TWILIO CONFIGURATION (Your Specific Keys) ---
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = "whatsapp:+14155238886"  # This is Twilio's Sandbox Number
POLICE_NUMBER = "whatsapp:+919606566174"

# --- FILE PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ensure the paths match your folder structure: backend/data/
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
    """Helper function to connect to the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name (row['id'])
    return conn

# ==========================================
# API ENDPOINTS
# ==========================================

# --- ENDPOINT 1: HOTSPOTS (For Heatmap) ---
@app.route('/api/hotspots', methods=['GET'])
def get_hotspots():
    """Returns all withdrawal locations to plot the Heatmap."""
    try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT 2: MULE HISTORY (For Investigator View) ---
@app.route('/api/mule_history', methods=['GET'])
def get_mule_history():
    """Returns the path taken by a specific criminal."""
    mule_id = request.args.get('mule_id') # e.g., ?mule_id=MULE_RINGLEADER_01
    
    if not mule_id:
        return jsonify({"error": "Please provide a mule_id"}), 400

    try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT 3: PREDICT NEXT MOVE (The AI) ---
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
        if mule_id in encoder.classes_:
            mule_encoded = encoder.transform([mule_id])[0]
        else:
            mule_encoded = 0 # If new mule, assume generic behavior

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

# --- ENDPOINT 4: PROCESS TRANSACTION (The Intervention + SMS) ---
@app.route('/api/process_transaction', methods=['POST'])
def process_transaction():
    """
    Simulates a live transaction.
    1. Checks if account is FROZEN.
    2. If suspicious -> BLOCKS account & ALERTS police (SMS).
    3. If safe -> Approves it.
    """
    data = request.json
    mule_id = data.get('mule_id')
    amount = data.get('amount')
    lat = data.get('lat')
    lng = data.get('long')

    try:
        conn = get_db_connection()
        
        # 1. CHECK: Is this account already blocked?
        cursor = conn.execute("SELECT status FROM complaints WHERE mule_account_id = ? LIMIT 1", (mule_id,))
        account = cursor.fetchone()
        
        if account and account['status'] == 'Frozen':
            conn.close()
            return jsonify({"status": "BLOCKED", "message": "Transaction Rejected: Account is Frozen."}), 403

        # 2. AI CHECK (Simplified Logic for Hackathon Demo)
        # Trigger alert if Amount > 50,000 AND it is a known "Ringleader" account
        is_suspicious = False
        if amount > 50000 and "MULE_RINGLEADER" in str(mule_id):
            is_suspicious = True

        if is_suspicious:
            # --- ACTION A: BLOCK THE ACCOUNT ---
            conn.execute("UPDATE complaints SET status = 'Frozen' WHERE mule_account_id = ?", (mule_id,))
            conn.commit()
            conn.close()

            # --- ACTION B: SEND SMS ALERT ---
            sms_status = "Not Sent"
            try:
                client = Client(TWILIO_SID, TWILIO_TOKEN)
                
                message_body = (
                    f"Hello Admin, verification code: {amount}. "
    f"Lat: {lat}"
                )
                
                message = client.messages.create(
                    body=message_body,
                    from_=TWILIO_FROM,
                    to=POLICE_NUMBER
                )
                sms_status = f"Sent (ID: {message.sid})"
                print(f"✅ SMS Sent to {POLICE_NUMBER}")
            except Exception as e:
                print(f"❌ SMS Failed: {e}")
                sms_status = "Failed (Check Twilio Keys)"

            return jsonify({
                "status": "INTERCEPTED",
                "alert": "High Risk Detected",
                "action": "Account Frozen & Police Notified",
                "sms_status": sms_status
            })

        # 3. IF SAFE
        conn.close()
        return jsonify({"status": "APPROVED", "message": "Transaction Successful"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RUN SERVER ---
if __name__ == '__main__':
    print("🚀 Backend running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)