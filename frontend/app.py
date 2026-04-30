import streamlit as st
import sqlite3
import hashlib
import random
import string
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os

# ==================== CONFIGURATION ====================
PASSWORD_REQUIREMENTS = {
    'min_length': 8,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digit': True,
    'require_special': True,
    'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?'
}

ROLES = {
    'User': {
        'level': 1,
        'name': 'Registered User',
        'access': ['Dashboard', 'View Complaints', 'Submit Complaint'],
        'description': 'Default access for registered citizens',
        'default': True
    },
    'Investigator': {
        'level': 2,
        'name': 'Crime Analyst/Investigator',
        'access': ['Dashboard', 'Heatmap', 'Predictor', 'Reports', 'Evidence Access'],
        'description': 'Deep dive analytics and investigation tools'
    },
    'Law Enforcement': {
        'level': 3,
        'name': 'Police Officer',
        'access': ['Dashboard', 'Heatmap', 'Predictor', 'Alerts', 'Reports', 'Deploy Teams'],
        'description': 'State/Local police with jurisdiction-based access'
    },
    'Bank Official': {
        'level': 3,
        'name': 'Bank/Financial Institution',
        'access': ['Dashboard', 'Alerts', 'Reports', 'Block Accounts', 'ATM Monitoring'],
        'description': 'Bank security and fraud prevention teams'
    },
    'I4C Officer': {
        'level': 4,
        'name': 'I4C Admin Officer',
        'access': ['Full Access', 'User Management', 'System Config', 'All Features'],
        'description': 'Ministry of Home Affairs - Full system access'
    }
}

EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'SENDER_EMAIL': 'babykalamadhu@gmail.com',
    'SENDER_PASSWORD': 'vatqllibqsnrqshw',  # ← NO SPACES!
}

# ==================== DATABASE FUNCTIONS ====================
def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'users.db')

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            jurisdiction TEXT,
            verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0
        )
    ''')
    
    # Create default admin
    admin_password = hashlib.sha256('Admin@123'.encode()).hexdigest()
    try:
        c.execute('''
            INSERT INTO users (email, password, role, name, jurisdiction, verified)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin@i4c.gov.in', admin_password, 'I4C Officer', 'System Admin', 'All India', 1))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()

# ==================== AUTH FUNCTIONS ====================
def validate_password(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < PASSWORD_REQUIREMENTS['min_length']:
        errors.append(f"At least {PASSWORD_REQUIREMENTS['min_length']} characters")
    
    if PASSWORD_REQUIREMENTS['require_uppercase'] and not re.search(r'[A-Z]', password):
        errors.append("One uppercase letter")
    
    if PASSWORD_REQUIREMENTS['require_lowercase'] and not re.search(r'[a-z]', password):
        errors.append("One lowercase letter")
    
    if PASSWORD_REQUIREMENTS['require_digit'] and not re.search(r'\d', password):
        errors.append("One digit")
    
    if PASSWORD_REQUIREMENTS['require_special']:
        special_chars = PASSWORD_REQUIREMENTS['special_chars']
        if not any(char in special_chars for char in password):
            errors.append("One special character")
    
    return len(errors) == 0, errors

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp, name="User"):
    """Send OTP via email - WITH DEBUG"""
    try:
        # Show OTP in terminal for debugging
        print(f"\n{'='*50}")
        print(f"📧 SENDING OTP TO: {email}")
        print(f"🔢 OTP CODE: {otp}")
        print(f"{'='*50}\n")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🔐 I4C Portal - Verification OTP'
        msg['From'] = EMAIL_CONFIG['SENDER_EMAIL']
        msg['To'] = email
        
        html = f"""
        <html><body style="font-family: Arial;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
            <h2 style="color: #0066cc;">🚨 I4C Cybercrime Portal</h2>
            <p>Dear {name},</p>
            <p>Your verification OTP is:</p>
            <div style="background: #f0f0f0; padding: 20px; text-align: center;">
                <h1 style="color: #0066cc; letter-spacing: 5px;">{otp}</h1>
            </div>
            <p>Valid for 10 minutes</p>
        </div>
        </body></html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        print(f"🔄 Connecting to {EMAIL_CONFIG['SMTP_SERVER']}...")
        with smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'], timeout=10) as server:
            print("🔐 Starting TLS...")
            server.starttls()
            
            print(f"🔑 Logging in as {EMAIL_CONFIG['SENDER_EMAIL']}...")
            server.login(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['SENDER_PASSWORD'])
            
            print("📤 Sending email...")
            server.send_message(msg)
            
        print("✅ Email sent successfully!\n")
        return True, "OTP sent successfully"
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Authentication failed: {str(e)}"
        print(f"❌ {error_msg}")
        return False, "Gmail authentication failed. Check App Password."
    except smtplib.SMTPException as e:
        error_msg = f"SMTP Error: {str(e)}"
        print(f"❌ {error_msg}")
        return False, f"Email sending failed: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        return False, f"Error: {str(e)}"

def store_otp(email, otp):
    """Store OTP in database"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('DELETE FROM otp_codes WHERE email = ?', (email,))
    expires_at = datetime.now() + timedelta(minutes=10)
    c.execute('INSERT INTO otp_codes (email, otp, expires_at) VALUES (?, ?, ?)', 
              (email, otp, expires_at))
    conn.commit()
    conn.close()

def verify_otp(email, otp):
    """Verify OTP"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''SELECT * FROM otp_codes 
                 WHERE email = ? AND otp = ? AND used = 0 AND expires_at > ?''',
              (email, otp, datetime.now()))
    result = c.fetchone()
    if result:
        c.execute('UPDATE otp_codes SET used = 1 WHERE id = ?', (result[0],))
        conn.commit()
    conn.close()
    return result is not None

def register_user(email, password, name, phone, role, jurisdiction):
    """Register new user"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute('''INSERT INTO users (email, password, role, name, phone, jurisdiction, verified)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (email, hashed, role, name, phone, jurisdiction, 1))
        conn.commit()
        conn.close()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Email already registered"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def login_user(email, password):
    """Login user"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    c.execute('SELECT * FROM users WHERE email = ? AND password = ? AND verified = 1',
              (email, hashed))
    user = c.fetchone()
    if user:
        c.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user[0]))
        conn.commit()
        user_data = {
            'id': user[0],
            'email': user[1],
            'role': user[3],
            'name': user[4],
            'phone': user[5],
            'jurisdiction': user[6],
            'access': ROLES.get(user[3], ROLES['User'])['access']
        }
        conn.close()
        return True, user_data
    conn.close()
    return False, None

def check_email_exists(email):
    """Check if email exists"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# ==================== STREAMLIT APP ====================
st.set_page_config(
    page_title="I4C Cybercrime Portal",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        margin: 2rem auto;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        max-width: 900px;
    }
    
    .main-header h1 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
    }
    
    .main-header h3 {
        color: #34495e;
        font-weight: normal;
        margin-bottom: 0.3rem;
    }
    
    .main-header p {
        color: #7f8c8d;
        font-size: 0.95rem;
    }
    
    /* Form container */
    .form-container {
        background: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        max-width: 600px;
        margin: 2rem auto;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 8px;
        color: #495057;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea !important;
        color: white !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 12px;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 2rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Role cards */
    .role-card {
        padding: 1rem;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .role-card:hover {
        border-color: #667eea;
        background-color: #f8f9ff;
        transform: translateX(5px);
    }
    
    .role-card.selected {
        border-color: #667eea;
        background-color: #e8ebff;
    }
    
    /* Password requirements */
    .password-req {
        font-size: 0.85rem;
        padding: 0.8rem;
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .password-req-item {
        margin: 0.3rem 0;
    }
    
    .req-met {
        color: #28a745;
    }
    
    .req-not-met {
        color: #dc3545;
    }
    
    /* Success/Error boxes */
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        color: #155724;
        margin: 1rem 0;
    }
    
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        color: #721c24;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        color: #0c5460;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize
init_db()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.temp_email = None
    st.session_state.temp_data = None

# ==================== NOT AUTHENTICATED ====================
if not st.session_state.authenticated:
    
    st.markdown("""
    <div class="main-header">
        <h1>🚨 I4C CYBERCRIME ANALYTICS PORTAL</h1>
        <h3>Ministry of Home Affairs</h3>
        <p>Predictive Analytics for Proactive Cybercrime Intervention</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    
    # LOGIN TAB
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            login_email = st.text_input("📧 Email", key="login_email")
            login_password = st.text_input("🔑 Password", type="password", key="login_password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 Login", type="primary", use_container_width=True):
                if login_email and login_password:
                    success, user_data = login_user(login_email, login_password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = user_data
                        st.success(f"✅ Welcome, {user_data['name']}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
                else:
                    st.warning("⚠️ Enter email and password")
            
            st.markdown("---")
            st.info("**Demo:** admin@i4c.gov.in / Admin@123")
    
    # REGISTER TAB
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 👤 Create Account")
            
            reg_name = st.text_input("👤 Full Name *", key="reg_name")
            reg_email = st.text_input("📧 Email *", key="reg_email")
            reg_phone = st.text_input("📱 Phone *", key="reg_phone")
            
            st.markdown("---")
            st.markdown("### 🔐 Password")
            
            reg_password = st.text_input("🔑 Password *", type="password", key="reg_password")
            reg_password_confirm = st.text_input("🔑 Confirm *", type="password", key="reg_password_confirm")
            
            if reg_password:
                st.markdown("**Requirements:**")
                col_req1, col_req2 = st.columns(2)
                with col_req1:
                    st.markdown(f"{'✅' if len(reg_password) >= 8 else '❌'} 8+ characters")
                    st.markdown(f"{'✅' if re.search(r'[A-Z]', reg_password) else '❌'} Uppercase")
                    st.markdown(f"{'✅' if re.search(r'[a-z]', reg_password) else '❌'} Lowercase")
                with col_req2:
                    st.markdown(f"{'✅' if re.search(r'\\d', reg_password) else '❌'} Number")
                    st.markdown(f"{'✅' if any(c in PASSWORD_REQUIREMENTS['special_chars'] for c in reg_password) else '❌'} Special")
                
                if reg_password_confirm:
                    if reg_password == reg_password_confirm:
                        st.success("✅ Passwords match")
                    else:
                        st.error("❌ Passwords don't match")
            
            st.markdown("---")
            st.markdown("### 🎭 Role")
            
            reg_role = st.radio("Select:", list(ROLES.keys()), index=0, 
                               format_func=lambda x: ROLES[x]['name'], key="reg_role")
            
            with st.expander(f"ℹ️ About {reg_role}"):
                st.write(ROLES[reg_role]['description'])
                for access in ROLES[reg_role]['access']:
                    st.write(f"✅ {access}")
            
            reg_jurisdiction = st.text_input("📍 Jurisdiction *", key="reg_jurisdiction")
            
            st.markdown("---")
            
            if st.button("📧 Send OTP", type="primary", use_container_width=True):
                errors = []
                
                if not reg_name or len(reg_name) < 3:
                    errors.append("Name too short")
                if not validate_email(reg_email):
                    errors.append("Invalid email")
                if check_email_exists(reg_email):
                    errors.append("Email exists")
                if not reg_phone or len(reg_phone) < 10:
                    errors.append("Invalid phone")
                if reg_password != reg_password_confirm:
                    errors.append("Passwords don't match")
                
                password_valid, password_errors = validate_password(reg_password)
                if not password_valid:
                    errors.extend(password_errors)
                
                if not reg_jurisdiction:
                    errors.append("Jurisdiction required")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    otp = generate_otp()
                    success, message = send_otp_email(reg_email, otp, reg_name)
                    
                    if success:
                        store_otp(reg_email, otp)
                        st.session_state.temp_email = reg_email
                        st.session_state.temp_data = {
                            'name': reg_name, 'phone': reg_phone,
                            'password': reg_password, 'role': reg_role,
                            'jurisdiction': reg_jurisdiction
                        }
                        st.success("✅ OTP sent! Check email")
                        
                        st.markdown("---")
                        st.markdown("### ✉️ Verify Email")
                        otp_input = st.text_input("🔢 Enter OTP", max_chars=6, key="otp_verify")
                        
                        col_v, col_r = st.columns(2)
                        with col_v:
                            if st.button("✅ Verify", type="primary", use_container_width=True):
                                if len(otp_input) == 6:
                                    if verify_otp(st.session_state.temp_email, otp_input):
                                        success, msg = register_user(
                                            st.session_state.temp_email,
                                            st.session_state.temp_data['password'],
                                            st.session_state.temp_data['name'],
                                            st.session_state.temp_data['phone'],
                                            st.session_state.temp_data['role'],
                                            st.session_state.temp_data['jurisdiction']
                                        )
                                        if success:
                                            st.success("🎉 Registered! Login now")
                                            st.balloons()
                                            st.session_state.temp_email = None
                                            st.session_state.temp_data = None
                                        else:
                                            st.error(f"❌ {msg}")
                                    else:
                                        st.error("❌ Invalid OTP")
                                else:
                                    st.warning("⚠️ Enter 6 digits")
                        
                        with col_r:
                            if st.button("🔄 Resend", use_container_width=True):
                                new_otp = generate_otp()
                                success, msg = send_otp_email(
                                    st.session_state.temp_email, new_otp,
                                    st.session_state.temp_data['name']
                                )
                                if success:
                                    store_otp(st.session_state.temp_email, new_otp)
                                    st.success("✅ New OTP sent")
                    else:
                        st.error(f"❌ {message}")

# ==================== AUTHENTICATED ====================
else:
    st.sidebar.success(f"👤 {st.session_state.user['name']}")
    st.sidebar.info(f"🎭 {st.session_state.user['role']}")
    st.sidebar.info(f"📍 {st.session_state.user['jurisdiction']}")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="primary"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()
    
    # Main welcome page after login
    st.markdown(f"# 🎯 Welcome, {st.session_state.user['name']}!")
    st.markdown(f"**Role:** {st.session_state.user['role']} | **Jurisdiction:** {st.session_state.user['jurisdiction']}")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📥 Complaints", "847", "+12%")
    with col2:
        st.metric("🎯 Predictions", "23", "+5")
    with col3:
        st.metric("🚨 Alerts", "8", "-2")
    with col4:
        st.metric("✅ Success Rate", "76%", "+3%")
    
    st.markdown("---")
    
    # BIG NAVIGATION BUTTONS
    st.markdown("## 🚀 Quick Navigation")
    
    nav_col1, nav_col2 = st.columns(2)
    
    with nav_col1:
        if st.button("🏠 GO TO DASHBOARD", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Dashboard.py")

        if st.button("📚 VIEW CRIME HEATMAP", use_container_width=True):
            st.switch_page("pages/2_Heatmap.py")

    with nav_col2:
        if st.button("🎯 GENERATE PREDICTIONS", use_container_width=True):
            st.switch_page("pages/3_Predictor.py")
        
        if st.button("🚨 VIEW ALERTS", use_container_width=True):
            st.switch_page("pages/4_Alerts.py")

        if st.button("📊 VIEW REPORTS", use_container_width=True):
            st.switch_page("pages/5_Reports.py")
    
    st.markdown("---")
    st.markdown("## 🔐 Your Access")
    for access in st.session_state.user['access']:
        st.write(f"✅ {access}")
    
    st.info("🎯 Use sidebar or buttons above to navigate!")
    st.info("📱 Check sidebar (left) for all available modules!")

st.sidebar.title("I4C Cybercrime Portal")
st.sidebar.markdown("Select a page from the sidebar to begin.")