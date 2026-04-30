"""
Utility functions for I4C Cybercrime Analytics Portal
Helper functions used across all pages
"""

import streamlit as st
from datetime import datetime
import hashlib

# ==================== AUTHENTICATION HELPERS ====================

def check_authentication():
    """Check if user is authenticated, redirect to login if not"""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("🔒 Please login first!")
        st.stop()
    return st.session_state.user

def get_user_role():
    """Get current user's role"""
    if 'user' in st.session_state and st.session_state.user:
        return st.session_state.user.get('role', 'User')
    return None

def has_permission(required_role: str) -> bool:
    """Check if user has required permission level"""
    role_hierarchy = {
        'User': 1,
        'Investigator': 2,
        'Law Enforcement': 3,
        'Bank Official': 3,
        'I4C Officer': 4
    }
    
    user_role = get_user_role()
    if not user_role:
        return False
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 999)
    
    return user_level >= required_level

# ==================== UI HELPERS ====================

def show_metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal"):
    """Display a metric card with consistent styling"""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)

def show_status_badge(status: str) -> str:
    """Return colored HTML badge for status"""
    colors = {
        'Active': '#28a745',
        'Under Investigation': '#ffc107',
        'Evidence Collected': '#17a2b8',
        'Account Frozen': '#fd7e14',
        'Resolved': '#6c757d',
        'Pending': '#dc3545',
        'Critical': '#dc3545',
        'High': '#fd7e14',
        'Medium': '#ffc107',
        'Low': '#28a745'
    }
    
    color = colors.get(status, '#6c757d')
    return f'<span style="background-color: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">{status}</span>'

def show_priority_badge(priority: str) -> str:
    """Return colored HTML badge for priority"""
    return show_status_badge(priority)

def format_currency(amount: float) -> str:
    """Format amount in Indian currency format"""
    if amount >= 10000000:  # 1 Crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 Lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.2f}"

def format_datetime(dt_string: str) -> str:
    """Format datetime string to readable format"""
    if not dt_string:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%d %b %Y, %I:%M %p")
    except:
        return dt_string

def format_date(dt_string: str) -> str:
    """Format date string"""
    if not dt_string:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%d %b %Y")
    except:
        return dt_string

# ==================== DATA HELPERS ====================

def get_severity_color(severity: str) -> str:
    """Get color code for severity level"""
    colors = {
        'Critical': '#dc3545',
        'High': '#fd7e14',
        'Medium': '#ffc107',
        'Low': '#28a745'
    }
    return colors.get(severity, '#6c757d')

def get_fraud_type_emoji(fraud_type: str) -> str:
    """Get emoji for fraud type"""
    emojis = {
        'UPI Fraud': '💳',
        'Credit Card Fraud': '💳',
        'Investment Scam': '📈',
        'Job Fraud': '💼',
        'Lottery Scam': '🎰',
        'Online Shopping Fraud': '🛒',
        'Phishing': '🎣',
        'Romance Scam': '💔',
        'Loan Fraud': '💰',
        'Cyber Extortion': '⚠️'
    }
    return emojis.get(fraud_type, '🚨')

def calculate_time_ago(dt_string: str) -> str:
    """Calculate human-readable time ago"""
    if not dt_string:
        return "Unknown"
    
    try:
        dt = datetime.fromisoformat(dt_string)
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 30:
            return f"{diff.days // 30} month(s) ago"
        elif diff.days > 0:
            return f"{diff.days} day(s) ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hour(s) ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minute(s) ago"
        else:
            return "Just now"
    except:
        return "Unknown"

# ==================== CHART HELPERS ====================

def get_chart_colors() -> list:
    """Get consistent color palette for charts"""
    return [
        '#667eea', '#764ba2', '#f093fb', '#4facfe',
        '#43e97b', '#fa709a', '#fee140', '#30cfd0'
    ]

def get_gradient_color(value: float, min_val: float, max_val: float) -> str:
    """Get color based on value gradient (green to red)"""
    if max_val == min_val:
        return '#28a745'
    
    ratio = (value - min_val) / (max_val - min_val)
    
    if ratio < 0.33:
        return '#28a745'  # Green
    elif ratio < 0.66:
        return '#ffc107'  # Yellow
    else:
        return '#dc3545'  # Red

# ==================== VALIDATION HELPERS ====================

def validate_phone(phone: str) -> bool:
    """Validate Indian phone number"""
    import re
    pattern = r'^(\+91[-\s]?)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_account_number(account: str) -> bool:
    """Validate bank account number"""
    return account.isdigit() and 9 <= len(account) <= 18

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    return text.strip()[:500]  # Limit length and trim

# ==================== NOTIFICATION HELPERS ====================

def show_success_message(message: str):
    """Show success notification"""
    st.success(f"✅ {message}")

def show_error_message(message: str):
    """Show error notification"""
    st.error(f"❌ {message}")

def show_warning_message(message: str):
    """Show warning notification"""
    st.warning(f"⚠️ {message}")

def show_info_message(message: str):
    """Show info notification"""
    st.info(f"ℹ️ {message}")

# ==================== EXPORT HELPERS ====================

def generate_report_filename(report_type: str) -> str:
    """Generate filename for exported reports"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"I4C_{report_type}_{timestamp}.csv"

# ==================== SESSION HELPERS ====================

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'page_loaded': False,
        'last_refresh': datetime.now(),
        'filters': {},
        'selected_items': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value