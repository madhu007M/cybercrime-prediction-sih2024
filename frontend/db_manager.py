"""
Database Manager for I4C Cybercrime Analytics Portal
Handles all database operations with optimized queries
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    """Centralized database management for all operations"""
    
    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.users_db = os.path.join(self.base_path, 'users.db')
        self.complaints_db = os.path.join(self.base_path, 'complaints.db')
        self.predictions_db = os.path.join(self.base_path, 'predictions.db')
        self.alerts_db = os.path.join(self.base_path, 'alerts.db')
    
    # ==================== USER OPERATIONS ====================
    
    def get_user_stats(self, user_role: str) -> Dict:
        """Get role-based statistics for dashboard"""
        stats = {
            'total_complaints': 0,
            'active_complaints': 0,
            'total_predictions': 0,
            'active_alerts': 0,
            'success_rate': 0,
            'amount_recovered': 0
        }
        
        # Complaints stats
        conn = sqlite3.connect(self.complaints_db)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM complaints')
        stats['total_complaints'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM complaints WHERE status != 'Resolved'")
        stats['active_complaints'] = c.fetchone()[0]
        
        c.execute("SELECT SUM(amount_lost) FROM complaints WHERE status = 'Resolved'")
        result = c.fetchone()[0]
        stats['amount_recovered'] = round(result * 0.68, 2) if result else 0  # 68% recovery rate
        
        conn.close()
        
        # Predictions stats
        conn = sqlite3.connect(self.predictions_db)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM predictions')
        stats['total_predictions'] = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM predictions WHERE prediction_accurate = 1')
        accurate = c.fetchone()[0]
        stats['success_rate'] = round((accurate / stats['total_predictions'] * 100), 1) if stats['total_predictions'] > 0 else 0
        
        conn.close()
        
        # Alerts stats
        conn = sqlite3.connect(self.alerts_db)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM alerts WHERE status = 'Active'")
        stats['active_alerts'] = c.fetchone()[0]
        
        conn.close()
        
        return stats
    
    # ==================== COMPLAINT OPERATIONS ====================
    
    def get_recent_complaints(self, limit: int = 10, status: Optional[str] = None) -> List[Dict]:
        """Get recent complaints with optional status filter"""
        conn = sqlite3.connect(self.complaints_db)
        c = conn.cursor()
        
        query = 'SELECT * FROM complaints'
        if status:
            query += f" WHERE status = '{status}'"
        query += ' ORDER BY complaint_date DESC LIMIT ?'
        
        c.execute(query, (limit,))
        rows = c.fetchall()
        
        complaints = []
        for row in rows:
            complaints.append({
                'id': row[0],
                'complaint_id': row[1],
                'victim_name': row[2],
                'victim_phone': row[3],
                'fraud_type': row[4],
                'amount_lost': row[5],
                'mule_account': row[6],
                'mule_bank': row[7],
                'complaint_date': row[8],
                'incident_date': row[9],
                'incident_location': row[10],
                'incident_city': row[11],
                'incident_state': row[12],
                'status': row[13],
                'priority': row[14]
            })
        
        conn.close()
        return complaints
    
    def get_complaints_by_city(self) -> Dict[str, int]:
        """Get complaint count by city for heatmap"""
        conn = sqlite3.connect(self.complaints_db)
        c = conn.cursor()
        
        c.execute('''
            SELECT incident_city, COUNT(*) 
            FROM complaints 
            GROUP BY incident_city 
            ORDER BY COUNT(*) DESC
        ''')
        
        city_data = {}
        for row in c.fetchall():
            city_data[row[0]] = row[1]
        
        conn.close()
        return city_data
    
    def get_complaints_by_fraud_type(self) -> Dict[str, int]:
        """Get complaint count by fraud type"""
        conn = sqlite3.connect(self.complaints_db)
        c = conn.cursor()
        
        c.execute('''
            SELECT fraud_type, COUNT(*) 
            FROM complaints 
            GROUP BY fraud_type 
            ORDER BY COUNT(*) DESC
        ''')
        
        fraud_data = {}
        for row in c.fetchall():
            fraud_data[row[0]] = row[1]
        
        conn.close()
        return fraud_data
    
    def get_complaint_by_id(self, complaint_id: str) -> Optional[Dict]:
        """Get single complaint details"""
        conn = sqlite3.connect(self.complaints_db)
        c = conn.cursor()
        
        c.execute('SELECT * FROM complaints WHERE complaint_id = ?', (complaint_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'complaint_id': row[1],
            'victim_name': row[2],
            'victim_phone': row[3],
            'fraud_type': row[4],
            'amount_lost': row[5],
            'mule_account': row[6],
            'mule_bank': row[7],
            'complaint_date': row[8],
            'incident_date': row[9],
            'incident_city': row[11],
            'incident_state': row[12],
            'status': row[13],
            'priority': row[14]
        }
    
    # ==================== PREDICTION OPERATIONS ====================
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict]:
        """Get recent ML predictions"""
        conn = sqlite3.connect(self.predictions_db)
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM predictions 
            ORDER BY prediction_date DESC 
            LIMIT ?
        ''', (limit,))
        
        predictions = []
        for row in c.fetchall():
            predictions.append({
                'prediction_id': row[1],
                'complaint_id': row[2],
                'mule_account': row[3],
                'method': row[4],
                'atm_1': row[5],
                'city_1': row[6],
                'confidence_1': row[7],
                'atm_2': row[8],
                'city_2': row[9],
                'confidence_2': row[10],
                'atm_3': row[11],
                'city_3': row[12],
                'confidence_3': row[13],
                'prediction_date': row[14],
                'status': row[15]
            })
        
        conn.close()
        return predictions
    
    def get_prediction_accuracy_stats(self) -> Dict:
        """Calculate prediction accuracy statistics"""
        conn = sqlite3.connect(self.predictions_db)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*), AVG(confidence_1), AVG(prediction_accurate) FROM predictions')
        row = c.fetchone()
        
        stats = {
            'total_predictions': row[0] or 0,
            'avg_confidence': round(row[1], 2) if row[1] else 0,
            'accuracy_rate': round((row[2] * 100), 1) if row[2] else 0
        }
        
        c.execute("SELECT prediction_method, COUNT(*) FROM predictions GROUP BY prediction_method")
        stats['by_method'] = {row[0]: row[1] for row in c.fetchall()}
        
        conn.close()
        return stats
    
    # ==================== ALERT OPERATIONS ====================
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """Get active alerts with optional severity filter"""
        conn = sqlite3.connect(self.alerts_db)
        c = conn.cursor()
        
        query = "SELECT * FROM alerts WHERE status = 'Active'"
        if severity:
            query += f" AND severity = '{severity}'"
        query += " ORDER BY created_at DESC"
        
        c.execute(query)
        
        alerts = []
        for row in c.fetchall():
            alerts.append({
                'alert_id': row[1],
                'alert_type': row[2],
                'severity': row[3],
                'title': row[4],
                'message': row[5],
                'location': row[8],
                'status': row[11],
                'created_at': row[12]
            })
        
        conn.close()
        return alerts
    
    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        conn = sqlite3.connect(self.alerts_db)
        c = conn.cursor()
        
        stats = {}
        
        c.execute("SELECT COUNT(*) FROM alerts WHERE status = 'Active'")
        stats['active'] = c.fetchone()[0]
        
        c.execute("SELECT severity, COUNT(*) FROM alerts WHERE status = 'Active' GROUP BY severity")
        stats['by_severity'] = {row[0]: row[1] for row in c.fetchall()}
        
        c.execute("SELECT COUNT(*) FROM alerts WHERE created_at > datetime('now', '-24 hours')")
        stats['last_24h'] = c.fetchone()[0]
        
        conn.close()
        return stats
    
    def acknowledge_alert(self, alert_id: str, user_email: str) -> bool:
        """Mark alert as acknowledged"""
        conn = sqlite3.connect(self.alerts_db)
        c = conn.cursor()
        
        try:
            c.execute('''
                UPDATE alerts 
                SET status = 'Acknowledged', 
                    acknowledged_at = ?,
                    assigned_to = ?
                WHERE alert_id = ?
            ''', (datetime.now().isoformat(), user_email, alert_id))
            
            conn.commit()
            success = c.rowcount > 0
        except Exception as e:
            print(f"Error acknowledging alert: {e}")
            success = False
        finally:
            conn.close()
        
        return success
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def get_time_series_data(self, days: int = 30) -> Dict:
        """Get time-series data for charts"""
        conn = sqlite3.connect(self.complaints_db)
        c = conn.cursor()
        
        c.execute('''
            SELECT DATE(complaint_date) as date, COUNT(*) as count
            FROM complaints
            WHERE complaint_date > datetime('now', '-' || ? || ' days')
            GROUP BY DATE(complaint_date)
            ORDER BY date
        ''', (days,))
        
        dates = []
        counts = []
        for row in c.fetchall():
            dates.append(row[0])
            counts.append(row[1])
        
        conn.close()
        
        return {'dates': dates, 'counts': counts}
    
    def get_fraud_amount_by_type(self) -> Dict:
        """Get total fraud amount by type"""
        conn = sqlite3.connect(self.complaints_db)
        c = conn.cursor()
        
        c.execute('''
            SELECT fraud_type, SUM(amount_lost) as total
            FROM complaints
            GROUP BY fraud_type
            ORDER BY total DESC
        ''')
        
        data = {row[0]: round(row[1], 2) for row in c.fetchall()}
        conn.close()
        
        return data
    
    # ==================== HEATMAP DATA ====================
    
    def get_crime_locations(self) -> List[Dict]:
        """Get all crime locations for heatmap visualization"""
        conn = sqlite3.connect(self.complaints_db)
        c = conn.cursor()
        
        c.execute('''
            SELECT incident_city, incident_state, COUNT(*) as count, 
                   AVG(amount_lost) as avg_amount, fraud_type
            FROM complaints
            GROUP BY incident_city, incident_state, fraud_type
        ''')
        
        locations = []
        for row in c.fetchall():
            locations.append({
                'city': row[0],
                'state': row[1],
                'count': row[2],
                'avg_amount': round(row[3], 2),
                'fraud_type': row[4]
            })
        
        conn.close()
        return locations

# Create singleton instance
db = DatabaseManager()

def map_complaint_data(complaint: Dict) -> Dict:
    """Map complaint data to standardized format"""
    fraud_type = complaint.get('fraud_type', 'Unknown')
    amount_raw = complaint.get('amount_lost', 0)
    city = complaint.get('incident_city', 'Unknown')
    date_raw = complaint.get('complaint_date', '')
    
    # Additional mapping logic if needed
    
    return {
        'fraud_type': fraud_type,
        'amount_lost': round(amount_raw, 2),
        'incident_city': city,
        'complaint_date': date_raw
    }