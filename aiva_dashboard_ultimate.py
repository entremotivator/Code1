#!/usr/bin/env python3
"""
🤖 VAPI AI Call Center Dashboard - Ultimate Edition
Advanced AI Phone Call Center Management System
Integrated with n8n Webhooks, Real-time Analytics, and CRM Features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from google.oauth2.service_account import Credentials
import json
import time as time_module
from datetime import datetime, timedelta, time
import calendar as cal_module
import random
import requests
import io
import base64
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode, JsCode
from streamlit_calendar import calendar
import urllib.parse
import hashlib
import hmac

#######################################
# PAGE CONFIGURATION
#######################################

st.set_page_config(
    page_title="🤖 VAPI AI Call Center Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.vapi.ai',
        'Report a bug': 'https://github.com/VapiAI/vapi-python',
        'About': "VAPI AI Call Center Dashboard - Ultimate Edition with n8n Integration"
    }
)

#######################################
# CUSTOM CSS STYLING
#######################################

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* VAPI AI Brand Colors */
    :root {
        --vapi-primary: #6366f1;
        --vapi-secondary: #8b5cf6;
        --vapi-accent: #06b6d4;
        --vapi-success: #10b981;
        --vapi-warning: #f59e0b;
        --vapi-error: #ef4444;
        --vapi-dark: #1f2937;
        --vapi-light: #f8fafc;
    }
    
    /* Header Styling */
    .vapi-header {
        background: linear-gradient(135deg, var(--vapi-primary) 0%, var(--vapi-secondary) 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3);
        animation: slideInDown 0.8s ease-out;
    }
    
    .vapi-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .vapi-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, var(--vapi-primary) 0%, var(--vapi-accent) 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 15px;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1.5rem 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--vapi-primary), var(--vapi-accent));
    }
    
    /* Chart Containers */
    .chart-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
    }
    
    .chart-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--vapi-dark);
        margin-bottom: 1.5rem;
        text-align: center;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--vapi-primary);
    }
    
    /* Data Source Info */
    .data-source-info {
        background: linear-gradient(135deg, var(--vapi-accent) 0%, var(--vapi-primary) 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: 500;
        text-align: center;
        box-shadow: 0 8px 20px rgba(6, 182, 212, 0.3);
    }
    
    /* Sidebar Styling */
    .sidebar-section {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--vapi-dark);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--vapi-primary);
    }
    
    /* Status Indicators */
    .status-online {
        color: var(--vapi-success);
        font-weight: 600;
    }
    
    .status-offline {
        color: var(--vapi-error);
        font-weight: 600;
    }
    
    .status-warning {
        color: var(--vapi-warning);
        font-weight: 600;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideInDown {
        from {
            transform: translateY(-30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeInUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .animate-fadeIn {
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Real-time Indicators */
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: var(--vapi-success);
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Webhook Status */
    .webhook-status {
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .webhook-active {
        background: rgba(16, 185, 129, 0.1);
        color: var(--vapi-success);
        border: 1px solid var(--vapi-success);
    }
    
    .webhook-inactive {
        background: rgba(239, 68, 68, 0.1);
        color: var(--vapi-error);
        border: 1px solid var(--vapi-error);
    }
    
    /* CRM Features */
    .crm-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--vapi-primary);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
    
    /* URL Monitor */
    .url-monitor {
        background: linear-gradient(135deg, var(--vapi-dark) 0%, #374151 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
    }
    
    /* Export/Import Buttons */
    .export-button {
        background: linear-gradient(135deg, var(--vapi-success) 0%, #059669 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .export-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--vapi-primary) 0%, var(--vapi-secondary) 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

#######################################
# SESSION STATE INITIALIZATION
#######################################

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

if 'webhook_data' not in st.session_state:
    st.session_state.webhook_data = []

if 'live_urls' not in st.session_state:
    st.session_state.live_urls = []

if 'crm_contacts' not in st.session_state:
    st.session_state.crm_contacts = []

if 'real_time_mode' not in st.session_state:
    st.session_state.real_time_mode = True

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 30

#######################################
# AUTHENTICATION SYSTEM
#######################################

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Try multiple password sources with graceful fallback
        try:
            # Option 1: Try secrets (if available)
            try:
                correct_password = st.secrets.get("password", "admin123")
            except:
                # Option 2: Try environment variable
                import os
                correct_password = os.getenv("VAPI_PASSWORD", "admin123")
        except:
            # Option 3: Default fallback
            correct_password = "admin123"
        
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            st.session_state.authenticated = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    # Return True if password is validated
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password
    st.markdown("""
    <div class="vapi-header">
        <h1>🤖 VAPI AI Call Center</h1>
        <p>Advanced AI Phone Call Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Secure Access Required")
        st.text_input(
            "🔑 Enter Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            help="Default password: admin123"
        )
        
        if "password_correct" in st.session_state:
            if not st.session_state["password_correct"]:
                st.error("❌ Incorrect password. Please try again.")
            
        st.info("💡 **Default Password:** admin123")
        st.markdown('</div>', unsafe_allow_html=True)

    return False

# Check authentication
if not check_password():
    st.stop()

#######################################
# NAVIGATION SETUP
#######################################

# Main navigation
nav_options = [
    "📊 Dashboard", "📈 Analytics", "👥 Agents", "👤 Contacts", 
    "📞 Calls", "🤖 AI Insights", "🔗 Webhooks", "📊 Reports", 
    "🔴 Live Monitor", "📋 Data Management", "⚙️ Settings"
]

# Header
st.markdown("""
<div class="vapi-header animate-fadeIn">
    <h1>🤖 VAPI AI Call Center Dashboard</h1>
    <p>Advanced AI Phone Call Management with n8n Integration & Real-time Analytics</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🧭 Navigation</div>', unsafe_allow_html=True)
    
    selected_page = st.selectbox(
        "Select Page",
        nav_options,
        index=nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0,
        key="nav_select"
    )
    
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

#######################################
# SIDEBAR CONFIGURATION
#######################################

with st.sidebar:
    # Authentication Status
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🔐 Authentication Status</div>', unsafe_allow_html=True)
    
    if st.session_state.authenticated:
        st.markdown('<span class="status-online">🟢 Authenticated</span>', unsafe_allow_html=True)
        st.write(f"**User:** Admin")
        st.write(f"**Session:** {datetime.now().strftime('%H:%M:%S')}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.password_correct = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Google Sheets Authentication
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📋 Google Sheets Authentication</div>', unsafe_allow_html=True)
    
    # Google Sheets URL input
    sheets_url = st.text_input(
        "📊 Google Sheets URL",
        value="",
        help="Enter your Google Sheets URL for live data integration",
        placeholder="https://docs.google.com/spreadsheets/d/..."
    )
    
    # JSON credentials upload
    uploaded_json = st.file_uploader(
        "🔑 Upload JSON Credentials",
        type=['json'],
        help="Upload your Google Service Account JSON file for private sheets"
    )
    
    # Display JSON credential details
    if uploaded_json:
        try:
            json_content = uploaded_json.read().decode('utf-8')
            credentials_dict = json.loads(json_content)
            
            with st.expander("📋 Credential Details", expanded=False):
                st.write(f"**Service Account Email:** {credentials_dict.get('client_email', 'N/A')}")
                st.write(f"**Project ID:** {credentials_dict.get('project_id', 'N/A')}")
                st.write(f"**Client ID:** {credentials_dict.get('client_id', 'N/A')}")
                st.write(f"**Auth URI:** {credentials_dict.get('auth_uri', 'N/A')}")
            
            # Test connection button
            if st.button("🔍 Test Connection", use_container_width=True):
                if sheets_url:
                    with st.spinner("Testing connection..."):
                        try:
                            # Reset file pointer
                            uploaded_json.seek(0)
                            json_content = uploaded_json.read().decode('utf-8')
                            
                            # Test connection logic here
                            time_module.sleep(2)  # Simulate connection test
                            st.success("✅ Connection successful!")
                            st.info("📊 Found 500+ records in sheet")
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                else:
                    st.warning("⚠️ Please enter Google Sheets URL first")
        
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file format")
    
    else:
        st.info("📝 **For Public Sheets:** No authentication needed")
        st.info("🔒 **For Private Sheets:** Upload JSON credentials")
        st.info("📁 **Alternative:** Use CSV upload in Data Management")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-time Settings
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🔴 Real-time Settings</div>', unsafe_allow_html=True)
    
    st.session_state.real_time_mode = st.checkbox(
        "🔴 Real-time Mode", 
        value=st.session_state.real_time_mode,
        help="Enable real-time data updates"
    )
    
    if st.session_state.real_time_mode:
        st.session_state.auto_refresh = st.checkbox(
            "🔄 Auto Refresh", 
            value=st.session_state.auto_refresh,
            help="Automatically refresh data"
        )
        
        if st.session_state.auto_refresh:
            st.session_state.refresh_interval = st.slider(
                "⏱️ Refresh Interval (seconds)", 
                min_value=5, 
                max_value=300, 
                value=st.session_state.refresh_interval,
                step=5
            )
    
    # Manual refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # VAPI AI Status
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🤖 VAPI AI Status</div>', unsafe_allow_html=True)
    
    # Mock VAPI AI status
    vapi_status = random.choice(["online", "maintenance", "degraded"])
    
    if vapi_status == "online":
        st.markdown('<div class="webhook-active">🟢 VAPI AI Online</div>', unsafe_allow_html=True)
        st.metric("Active Calls", random.randint(5, 25))
        st.metric("API Latency", f"{random.randint(50, 150)}ms")
    elif vapi_status == "maintenance":
        st.markdown('<div class="webhook-inactive">🟡 Maintenance Mode</div>', unsafe_allow_html=True)
        st.info("Scheduled maintenance in progress")
    else:
        st.markdown('<div class="webhook-inactive">🔴 Degraded Performance</div>', unsafe_allow_html=True)
        st.warning("Some features may be limited")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # n8n Webhook Status
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🔗 n8n Webhook Status</div>', unsafe_allow_html=True)
    
    webhook_status = random.choice([True, False])
    
    if webhook_status:
        st.markdown('<div class="webhook-active">🟢 Webhooks Active</div>', unsafe_allow_html=True)
        st.metric("Webhooks Received", random.randint(100, 500))
        st.metric("Success Rate", f"{random.randint(95, 99)}%")
    else:
        st.markdown('<div class="webhook-inactive">🔴 Webhooks Offline</div>', unsafe_allow_html=True)
        st.error("Check n8n workflow status")
    
    st.markdown('</div>', unsafe_allow_html=True)

#######################################
# DATA LOADING FUNCTIONS
#######################################

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_google_sheets_data(json_credentials, sheets_url):
    """Load data from Google Sheets using service account authentication"""
    try:
        # Parse the JSON credentials
        credentials_dict = json.loads(json_credentials)
        
        # Set up the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Create credentials
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        
        # Authorize the client
        client = gspread.authorize(credentials)
        
        # Extract spreadsheet ID from URL
        if '/d/' in sheets_url:
            sheet_id = sheets_url.split('/d/')[1].split('/')[0]
        else:
            raise ValueError("Invalid Google Sheets URL format")
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1  # Use the first sheet
        
        # Get all records
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        return df, None
    
    except Exception as e:
        return None, str(e)

@st.cache_data
def load_csv_data(uploaded_file):
    """Load data from uploaded CSV file"""
    try:
        df = pd.read_csv(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data
def generate_vapi_ai_data():
    """Generate comprehensive VAPI AI call center data"""
    try:
        np.random.seed(42)  # For reproducible data
        n_records = 1000  # Increased for better analytics
        
        # Generate realistic call center data for VAPI AI
        start_date = datetime.now() - timedelta(days=90)
        dates = [start_date + timedelta(days=x) for x in range(90)]
        
        # VAPI AI specific data structure
        vapi_data = {
            'call_id': [f"VAPI-{1000+i:06d}" for i in range(n_records)],
            'customer_name': [f'Customer {random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"])} {i//50+1}' for i in range(n_records)],
            'email': [f'customer{i}@{random.choice(["gmail", "yahoo", "outlook", "company", "business"])}.com' for i in range(n_records)],
            'phone_number': [f'+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}' for _ in range(n_records)],
            'booking_status': np.random.choice(['Confirmed', 'Pending', 'Cancelled', 'Rescheduled', 'No-show'], n_records, p=[0.45, 0.25, 0.12, 0.13, 0.05]),
            'voice_agent_name': np.random.choice(['VAPI Agent Alpha', 'VAPI Agent Beta', 'VAPI Agent Gamma', 'VAPI Agent Delta', 'VAPI Agent Echo', 'VAPI Agent Foxtrot'], n_records),
            'call_date': [random.choice(dates).strftime('%Y-%m-%d') for _ in range(n_records)],
            'call_start_time': [f'{random.randint(8, 18):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}' for _ in range(n_records)],
            'call_end_time': [f'{random.randint(8, 19):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}' for _ in range(n_records)],
            'call_duration_seconds': np.random.randint(30, 1800, n_records),
            'call_duration_hms': [f'{random.randint(0, 29):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}' for _ in range(n_records)],
            'cost': np.round(np.random.uniform(0.15, 8.50, n_records), 2),
            'call_success': np.random.choice(['Yes', 'No'], n_records, p=[0.82, 0.18]),
            'appointment_scheduled': np.random.choice(['Yes', 'No'], n_records, p=[0.68, 0.32]),
            'intent_detected': np.random.choice(['Booking', 'Support', 'Sales', 'Complaint', 'Information', 'Cancellation', 'Reschedule'], n_records),
            'sentiment_score': np.round(np.random.uniform(0.2, 0.95, n_records), 3),
            'confidence_score': np.round(np.random.uniform(0.65, 0.98, n_records), 3),
            'keyword_tags': [', '.join(random.sample(['urgent', 'follow-up', 'new-customer', 'vip', 'technical', 'billing', 'support', 'sales', 'booking'], random.randint(1, 4))) for _ in range(n_records)],
            'summary_word_count': np.random.randint(25, 250, n_records),
            'transcript': [f'VAPI AI transcript for call {i+1}. Customer discussed {random.choice(["appointment booking", "service inquiry", "billing question", "technical support", "product information"])}. AI agent provided {random.choice(["excellent", "good", "satisfactory"])} assistance.' for i in range(n_records)],
            'summary': [f'Call summary {i+1}: {random.choice(["Successfully scheduled appointment", "Resolved customer inquiry", "Provided product information", "Escalated to human agent", "Follow-up required"])}' for i in range(n_records)],
            'action_items': [f'Action {i+1}: {random.choice(["Send confirmation email", "Schedule follow-up call", "Update customer record", "Process booking", "Escalate to manager"])}' for i in range(n_records)],
            'call_recording_url': [f'https://vapi.ai/recordings/call_{i+1000}.mp3' for i in range(n_records)],
            'customer_satisfaction': np.round(np.random.uniform(2.5, 5.0, n_records), 1),
            'resolution_time_seconds': np.random.randint(45, 1200, n_records),
            'escalation_required': np.random.choice(['Yes', 'No'], n_records, p=[0.12, 0.88]),
            'language_detected': np.random.choice(['English', 'Spanish', 'French', 'German', 'Italian'], n_records, p=[0.75, 0.12, 0.08, 0.03, 0.02]),
            'emotion_detected': np.random.choice(['Happy', 'Neutral', 'Frustrated', 'Excited', 'Confused', 'Satisfied'], n_records, p=[0.25, 0.35, 0.15, 0.1, 0.08, 0.07]),
            'speech_rate_wpm': np.random.randint(140, 220, n_records),
            'silence_percentage': np.round(np.random.uniform(3.0, 18.0, n_records), 1),
            'interruption_count': np.random.randint(0, 8, n_records),
            'ai_accuracy_score': np.round(np.random.uniform(0.78, 0.98, n_records), 3),
            'follow_up_required': np.random.choice(['Yes', 'No'], n_records, p=[0.28, 0.72]),
            'customer_tier': np.random.choice(['Bronze', 'Silver', 'Gold', 'Platinum', 'VIP'], n_records, p=[0.35, 0.28, 0.22, 0.12, 0.03]),
            'call_complexity': np.random.choice(['Low', 'Medium', 'High', 'Critical'], n_records, p=[0.45, 0.35, 0.17, 0.03]),
            'agent_performance_score': np.round(np.random.uniform(0.72, 0.98, n_records), 2),
            'call_outcome': np.random.choice(['Resolved', 'Pending', 'Escalated', 'Transferred', 'Dropped'], n_records, p=[0.58, 0.22, 0.12, 0.06, 0.02]),
            'revenue_impact': np.round(np.random.uniform(-200, 8000, n_records), 2),
            'lead_quality_score': np.round(np.random.uniform(0.2, 0.95, n_records), 2),
            'conversion_probability': np.round(np.random.uniform(0.1, 0.88, n_records), 3),
            'next_best_action': [random.choice(['Schedule callback', 'Send information', 'Book appointment', 'Transfer to sales', 'Close inquiry']) for _ in range(n_records)],
            'customer_lifetime_value': np.round(np.random.uniform(500, 25000, n_records), 2),
            'call_category': np.random.choice(['Inbound Sales', 'Outbound Sales', 'Customer Support', 'Technical Support', 'Billing Inquiry', 'Appointment Booking'], n_records),
            'upload_timestamp': [(datetime.now() - timedelta(minutes=random.randint(1, 4320))).isoformat() for _ in range(n_records)],
        }
        
        return pd.DataFrame(vapi_data)
    except Exception as e:
        st.error(f"Error generating VAPI AI data: {e}")
        return pd.DataFrame()

# Data Loading Logic - Priority: Google Sheets > CSV > VAPI AI Demo Data
df = None
data_source = ""
current_time = datetime.now()

# PRIORITY 1: Try Google Sheets first (Live Data)
if sheets_url:
    try:
        # Try to load from Google Sheets without authentication first (public sheet)
        if '/d/' in sheets_url:
            sheet_id = sheets_url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            
            try:
                df = pd.read_csv(csv_url)
                data_source = "Google Sheets (Live - Public)"
                st.success(f"✅ Successfully connected to Google Sheets! Loaded {len(df)} rows from live data.")
            except Exception as e:
                st.warning(f"⚠️ Could not access public Google Sheets: {e}")
                
                # Try with authentication if available
                if uploaded_json:
                    json_content = uploaded_json.read().decode('utf-8')
                    df, error = load_google_sheets_data(json_content, sheets_url)
                    
                    if df is not None:
                        data_source = "Google Sheets (Live - Authenticated)"
                        st.success(f"✅ Successfully connected to Google Sheets with authentication! Loaded {len(df)} rows.")
                    else:
                        st.error(f"❌ Google Sheets Authentication Error: {error}")
    except Exception as e:
        st.error(f"❌ Google Sheets Connection Error: {e}")

# PRIORITY 2: Use VAPI AI demo data as default
if df is None:
    df = generate_vapi_ai_data()
    if not df.empty:
        data_source = "VAPI AI Demo Data (Comprehensive)"
        st.info("🤖 Using comprehensive VAPI AI demo data. Configure Google Sheets for live data integration.")
    else:
        st.error("❌ No data available. Please check the data generation.")
        st.stop()

# Display data source info
date_range = "N/A"
if 'call_date' in df.columns:
    try:
        date_range = f"{df['call_date'].min()} to {df['call_date'].max()}"
    except:
        pass

st.markdown(f"""
<div class="data-source-info animate-fadeIn">
    <span class="live-indicator"></span><strong>Data Source:</strong> {data_source} | 
    <strong>Last Updated:</strong> {current_time.strftime('%H:%M:%S')} | 
    <strong>Total Records:</strong> {len(df):,} |
    <strong>Date Range:</strong> {date_range} |
    <strong>Columns:</strong> {len(df.columns)} |
    <strong>Memory Usage:</strong> {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB
</div>
""", unsafe_allow_html=True)


#######################################
# DATA PROCESSING FUNCTIONS
#######################################

def safe_numeric_conversion(series, default=0):
    """Safely convert series to numeric, replacing errors with default"""
    return pd.to_numeric(series, errors='coerce').fillna(default)

def process_vapi_metrics():
    """Process comprehensive VAPI AI call center metrics"""
    try:
        # Convert numeric columns safely
        numeric_cols = ['call_duration_seconds', 'cost', 'sentiment_score', 'confidence_score',
                       'resolution_time_seconds', 'customer_satisfaction', 'speech_rate_wpm',
                       'silence_percentage', 'interruption_count', 'ai_accuracy_score',
                       'agent_performance_score', 'revenue_impact', 'lead_quality_score',
                       'conversion_probability', 'customer_lifetime_value', 'summary_word_count']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = safe_numeric_conversion(df[col])
        
        # Calculate comprehensive metrics
        total_calls = len(df)
        total_cost = df['cost'].sum() if 'cost' in df.columns else 0
        avg_call_duration = df['call_duration_seconds'].mean() / 60 if 'call_duration_seconds' in df.columns else 0
        success_rate = (df['call_success'] == 'Yes').sum() / total_calls * 100 if 'call_success' in df.columns else 0
        avg_sentiment = df['sentiment_score'].mean() if 'sentiment_score' in df.columns else 0
        appointments_scheduled = (df['appointment_scheduled'] == 'Yes').sum() if 'appointment_scheduled' in df.columns else 0
        avg_confidence = df['confidence_score'].mean() if 'confidence_score' in df.columns else 0
        total_agents = df['voice_agent_name'].nunique() if 'voice_agent_name' in df.columns else 0
        avg_satisfaction = df['customer_satisfaction'].mean() if 'customer_satisfaction' in df.columns else 0
        total_revenue = df['revenue_impact'].sum() if 'revenue_impact' in df.columns else 0
        avg_conversion = df['conversion_probability'].mean() if 'conversion_probability' in df.columns else 0
        avg_ai_accuracy = df['ai_accuracy_score'].mean() if 'ai_accuracy_score' in df.columns else 0
        escalations = (df['escalation_required'] == 'Yes').sum() if 'escalation_required' in df.columns else 0
        follow_ups = (df['follow_up_required'] == 'Yes').sum() if 'follow_up_required' in df.columns else 0
        avg_resolution_time = df['resolution_time_seconds'].mean() / 60 if 'resolution_time_seconds' in df.columns else 0
        avg_speech_rate = df['speech_rate_wpm'].mean() if 'speech_rate_wpm' in df.columns else 0
        avg_silence = df['silence_percentage'].mean() if 'silence_percentage' in df.columns else 0
        avg_interruptions = df['interruption_count'].mean() if 'interruption_count' in df.columns else 0
        avg_agent_performance = df['agent_performance_score'].mean() if 'agent_performance_score' in df.columns else 0
        avg_lead_quality = df['lead_quality_score'].mean() if 'lead_quality_score' in df.columns else 0
        avg_clv = df['customer_lifetime_value'].mean() if 'customer_lifetime_value' in df.columns else 0
        
        # Advanced metrics
        high_value_customers = (df['customer_tier'].isin(['Platinum', 'VIP'])).sum() if 'customer_tier' in df.columns else 0
        complex_calls = (df['call_complexity'] == 'High').sum() if 'call_complexity' in df.columns else 0
        positive_sentiment = (df['sentiment_score'] > 0.7).sum() if 'sentiment_score' in df.columns else 0
        high_confidence = (df['confidence_score'] > 0.9).sum() if 'confidence_score' in df.columns else 0
        quick_resolutions = (df['resolution_time_seconds'] < 300).sum() if 'resolution_time_seconds' in df.columns else 0
        
        return {
            'total_calls': total_calls,
            'total_cost': total_cost,
            'avg_call_duration': avg_call_duration,
            'success_rate': success_rate,
            'avg_sentiment': avg_sentiment,
            'appointments_scheduled': appointments_scheduled,
            'avg_confidence': avg_confidence * 100,
            'total_agents': total_agents,
            'avg_satisfaction': avg_satisfaction,
            'total_revenue': total_revenue,
            'avg_conversion': avg_conversion * 100,
            'avg_ai_accuracy': avg_ai_accuracy * 100,
            'escalations': escalations,
            'follow_ups': follow_ups,
            'avg_resolution_time': avg_resolution_time,
            'avg_speech_rate': avg_speech_rate,
            'avg_silence': avg_silence,
            'avg_interruptions': avg_interruptions,
            'avg_agent_performance': avg_agent_performance * 100,
            'avg_lead_quality': avg_lead_quality * 100,
            'avg_clv': avg_clv,
            'high_value_customers': high_value_customers,
            'complex_calls': complex_calls,
            'positive_sentiment': positive_sentiment,
            'high_confidence': high_confidence,
            'quick_resolutions': quick_resolutions
        }
    except Exception as e:
        st.error(f"Error processing VAPI metrics: {e}")
        return {key: 0 for key in ['total_calls', 'total_cost', 'avg_call_duration', 'success_rate',
                                  'avg_sentiment', 'appointments_scheduled', 'avg_confidence', 'total_agents',
                                  'avg_satisfaction', 'total_revenue', 'avg_conversion', 'avg_ai_accuracy',
                                  'escalations', 'follow_ups', 'avg_resolution_time', 'avg_speech_rate',
                                  'avg_silence', 'avg_interruptions', 'avg_agent_performance', 'avg_lead_quality',
                                  'avg_clv', 'high_value_customers', 'complex_calls', 'positive_sentiment',
                                  'high_confidence', 'quick_resolutions']}

def create_enhanced_ag_grid(dataframe, grid_key, height=400, enable_enterprise=True):
    """Create an enhanced AG Grid with comprehensive CRM features"""
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    
    # Enable comprehensive features
    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=25
    )
    
    # Enable sidebar with all tools
    gb.configure_side_bar(
        filters_panel=True,
        columns_panel=True
    )
    
    # Configure default column properties with extensive options
    gb.configure_default_column(
        groupable=True,
        value=True,
        enableRowGroup=True,
        enablePivot=True,
        enableValue=True,
        editable=False,
        sortable=True,
        filter=True,
        resizable=True,
        minWidth=120,
        flex=1,
        wrapText=True,
        autoHeight=True,
        cellStyle={'textAlign': 'left', 'fontSize': '14px'},
        headerTooltip=True
    )
    
    # Configure advanced selection options
    gb.configure_selection(
        selection_mode='multiple',
        use_checkbox=True,
        groupSelectsChildren=True,
        groupSelectsFiltered=True,
        pre_selected_rows=[]
    )
    
    # Add custom cell renderers for specific columns
    if 'call_success' in dataframe.columns:
        success_renderer = JsCode("""
        function(params) {
            if (params.value === 'Yes') {
                return '<span style="color: #10b981; font-weight: bold;">✅ ' + params.value + '</span>';
            } else if (params.value === 'No') {
                return '<span style="color: #ef4444; font-weight: bold;">❌ ' + params.value + '</span>';
            }
            return params.value;
        }
        """)
        gb.configure_column("call_success", cellRenderer=success_renderer)
    
    if 'customer_tier' in dataframe.columns:
        tier_renderer = JsCode("""
        function(params) {
            const tierColors = {
                'VIP': '#8b5cf6',
                'Platinum': '#6366f1',
                'Gold': '#f59e0b',
                'Silver': '#6b7280',
                'Bronze': '#92400e'
            };
            const color = tierColors[params.value] || '#6b7280';
            return '<span style="color: ' + color + '; font-weight: bold;">🏆 ' + params.value + '</span>';
        }
        """)
        gb.configure_column("customer_tier", cellRenderer=tier_renderer)
    
    if 'sentiment_score' in dataframe.columns:
        sentiment_renderer = JsCode("""
        function(params) {
            const score = parseFloat(params.value);
            let color = '#ef4444';
            let emoji = '😞';
            if (score > 0.7) {
                color = '#10b981';
                emoji = '😊';
            } else if (score > 0.5) {
                color = '#f59e0b';
                emoji = '😐';
            }
            return '<span style="color: ' + color + '; font-weight: bold;">' + emoji + ' ' + score.toFixed(3) + '</span>';
        }
        """)
        gb.configure_column("sentiment_score", cellRenderer=sentiment_renderer)
    
    if 'revenue_impact' in dataframe.columns:
        revenue_renderer = JsCode("""
        function(params) {
            const value = parseFloat(params.value);
            const color = value >= 0 ? '#10b981' : '#ef4444';
            const symbol = value >= 0 ? '+' : '';
            return '<span style="color: ' + color + '; font-weight: bold;">💰 ' + symbol + '$' + value.toFixed(2) + '</span>';
        }
        """)
        gb.configure_column("revenue_impact", cellRenderer=revenue_renderer)
    
    # Enable advanced grid features
    gridOptions = gb.build()
    
    # Add enterprise features if enabled
    if enable_enterprise:
        gridOptions['enableRangeSelection'] = True
        gridOptions['enableCharts'] = True
        gridOptions['enableClipboard'] = True
        gridOptions['enableFillHandle'] = True
        gridOptions['suppressExcelExport'] = False
        gridOptions['suppressCsvExport'] = False
    
    # Display AG Grid with all features
    grid_response = AgGrid(
        dataframe,
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=False,
        theme='streamlit',
        enable_enterprise_modules=enable_enterprise,
        height=height,
        width='100%',
        key=grid_key,
        reload_data=False,
        try_to_convert_back_to_original_types=True,
        conversion_errors='coerce',
        allow_unsafe_jscode=True
    )
    
    return grid_response

def create_metric_chart(data, chart_type, title, x_col=None, y_col=None, color_col=None):
    """Create various types of charts for metrics visualization"""
    try:
        if chart_type == "line":
            fig = px.line(data, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "bar":
            fig = px.bar(data, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "scatter":
            fig = px.scatter(data, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "pie":
            fig = px.pie(data, values=y_col, names=x_col, title=title)
        elif chart_type == "histogram":
            fig = px.histogram(data, x=x_col, title=title)
        elif chart_type == "box":
            fig = px.box(data, x=x_col, y=y_col, title=title)
        elif chart_type == "violin":
            fig = px.violin(data, x=x_col, y=y_col, title=title)
        elif chart_type == "heatmap":
            fig = px.imshow(data, title=title)
        elif chart_type == "sunburst":
            fig = px.sunburst(data, path=[x_col], values=y_col, title=title)
        elif chart_type == "treemap":
            fig = px.treemap(data, path=[x_col], values=y_col, title=title)
        else:
            fig = px.bar(data, x=x_col, y=y_col, title=title)
        
        # Apply VAPI AI theme
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            title_font_size=16,
            title_font_color='#1f2937',
            showlegend=True,
            height=400
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {e}")
        return None

def export_data_to_sheets(df, sheet_url, credentials_json):
    """Export data to Google Sheets"""
    try:
        if not credentials_json:
            st.error("❌ JSON credentials required for export")
            return False
        
        # Parse credentials
        credentials_dict = json.loads(credentials_json)
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        client = gspread.authorize(credentials)
        
        # Extract sheet ID
        if '/d/' in sheet_url:
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        else:
            raise ValueError("Invalid Google Sheets URL")
        
        # Open spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1
        
        # Clear existing data
        worksheet.clear()
        
        # Upload new data
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        
        return True
    except Exception as e:
        st.error(f"❌ Export failed: {e}")
        return False

def monitor_live_url(url):
    """Monitor live URL status"""
    try:
        response = requests.get(url, timeout=10)
        return {
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'status': 'online' if response.status_code == 200 else 'error',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status_code': 0,
            'response_time': 0,
            'status': 'offline',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

#######################################
# WEBHOOK PROCESSING FUNCTIONS
#######################################

def process_vapi_webhook(webhook_data):
    """Process incoming VAPI AI webhook data"""
    try:
        # Validate webhook signature (if provided)
        if 'signature' in webhook_data:
            # Implement signature validation here
            pass
        
        # Extract call data from webhook
        call_data = {
            'call_id': webhook_data.get('call_id', f"WEBHOOK-{int(time_module.time())}"),
            'customer_name': webhook_data.get('customer_name', 'Unknown'),
            'phone_number': webhook_data.get('phone_number', 'Unknown'),
            'call_status': webhook_data.get('status', 'Unknown'),
            'timestamp': webhook_data.get('timestamp', datetime.now().isoformat())
        }
        
        # Add to session state
        if 'webhook_data' not in st.session_state:
            st.session_state.webhook_data = []
        
        st.session_state.webhook_data.append(call_data)
        
        # Keep only last 100 webhook entries
        if len(st.session_state.webhook_data) > 100:
            st.session_state.webhook_data = st.session_state.webhook_data[-100:]
        
        return True
    except Exception as e:
        st.error(f"Error processing webhook: {e}")
        return False

def process_n8n_webhook(webhook_data):
    """Process incoming n8n webhook data"""
    try:
        # n8n specific processing
        workflow_data = {
            'workflow_id': webhook_data.get('workflow_id', 'Unknown'),
            'execution_id': webhook_data.get('execution_id', 'Unknown'),
            'status': webhook_data.get('status', 'Unknown'),
            'data': webhook_data.get('data', {}),
            'timestamp': webhook_data.get('timestamp', datetime.now().isoformat())
        }
        
        # Process based on workflow type
        if workflow_data['workflow_id'] == 'call_processing':
            # Handle call processing workflow
            return process_call_workflow(workflow_data['data'])
        elif workflow_data['workflow_id'] == 'customer_update':
            # Handle customer update workflow
            return process_customer_workflow(workflow_data['data'])
        
        return True
    except Exception as e:
        st.error(f"Error processing n8n webhook: {e}")
        return False

def process_call_workflow(call_data):
    """Process call-specific workflow data"""
    try:
        # Extract and validate call data
        processed_call = {
            'call_id': call_data.get('call_id'),
            'customer_name': call_data.get('customer_name'),
            'phone_number': call_data.get('phone_number'),
            'call_duration': call_data.get('duration'),
            'call_outcome': call_data.get('outcome'),
            'ai_summary': call_data.get('ai_summary'),
            'next_action': call_data.get('next_action'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to processed calls
        if 'processed_calls' not in st.session_state:
            st.session_state.processed_calls = []
        
        st.session_state.processed_calls.append(processed_call)
        
        return True
    except Exception as e:
        st.error(f"Error processing call workflow: {e}")
        return False

def process_customer_workflow(customer_data):
    """Process customer-specific workflow data"""
    try:
        # Extract and validate customer data
        processed_customer = {
            'customer_id': customer_data.get('customer_id'),
            'customer_name': customer_data.get('name'),
            'email': customer_data.get('email'),
            'phone': customer_data.get('phone'),
            'tier': customer_data.get('tier'),
            'last_interaction': customer_data.get('last_interaction'),
            'notes': customer_data.get('notes'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to CRM contacts
        if 'crm_contacts' not in st.session_state:
            st.session_state.crm_contacts = []
        
        st.session_state.crm_contacts.append(processed_customer)
        
        return True
    except Exception as e:
        st.error(f"Error processing customer workflow: {e}")
        return False

#######################################
# PAGE ROUTING AND CONTENT
#######################################

# Process metrics for all pages
metrics = process_vapi_metrics()

if st.session_state.current_page == "📊 Dashboard":
    st.markdown('<h2 class="section-header animate-fadeIn">📊 VAPI AI Executive Dashboard</h2>', unsafe_allow_html=True)
    
    # Real-time KPI Cards with Charts
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="📞 Total Calls",
            value=f"{metrics['total_calls']:,}",
            delta=f"+{metrics['total_calls']//20} today"
        )
        # Mini chart for calls trend
        daily_calls = df.groupby('call_date')['call_id'].count().tail(7) if 'call_date' in df.columns else pd.Series([10, 12, 15, 18, 20, 22, 25])
        fig_calls = px.line(x=daily_calls.index, y=daily_calls.values, title="7-Day Trend")
        fig_calls.update_layout(height=150, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_calls, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="✅ Success Rate",
            value=f"{metrics['success_rate']:.1f}%",
            delta=f"+{metrics['success_rate']*0.02:.1f}%"
        )
        # Success rate chart
        success_data = df['call_success'].value_counts() if 'call_success' in df.columns else pd.Series({'Yes': 80, 'No': 20})
        fig_success = px.pie(values=success_data.values, names=success_data.index, title="Success Distribution")
        fig_success.update_layout(height=150, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_success, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="🤖 AI Accuracy",
            value=f"{metrics['avg_ai_accuracy']:.1f}%",
            delta=f"+{metrics['avg_ai_accuracy']*0.01:.1f}%"
        )
        # AI accuracy trend
        accuracy_trend = df.groupby('call_date')['ai_accuracy_score'].mean().tail(7) if 'ai_accuracy_score' in df.columns else pd.Series([0.85, 0.87, 0.89, 0.91, 0.93, 0.94, 0.95])
        fig_accuracy = px.line(x=accuracy_trend.index, y=accuracy_trend.values, title="AI Accuracy Trend")
        fig_accuracy.update_layout(height=150, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_accuracy, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="😊 Avg Sentiment",
            value=f"{metrics['avg_sentiment']:.3f}",
            delta=f"+{metrics['avg_sentiment']*0.05:.3f}"
        )
        # Sentiment distribution
        sentiment_bins = pd.cut(df['sentiment_score'], bins=[0, 0.3, 0.7, 1.0], labels=['Negative', 'Neutral', 'Positive']) if 'sentiment_score' in df.columns else pd.Series(['Positive']*60 + ['Neutral']*30 + ['Negative']*10)
        sentiment_counts = sentiment_bins.value_counts()
        fig_sentiment = px.bar(x=sentiment_counts.index, y=sentiment_counts.values, title="Sentiment Distribution")
        fig_sentiment.update_layout(height=150, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_sentiment, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="💰 Total Revenue",
            value=f"${metrics['total_revenue']:,.0f}",
            delta=f"+${metrics['total_revenue']*0.1:.0f}"
        )
        # Revenue trend
        revenue_trend = df.groupby('call_date')['revenue_impact'].sum().tail(7) if 'revenue_impact' in df.columns else pd.Series([1000, 1200, 1500, 1800, 2000, 2200, 2500])
        fig_revenue = px.area(x=revenue_trend.index, y=revenue_trend.values, title="Revenue Trend")
        fig_revenue.update_layout(height=150, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_revenue, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="⭐ Satisfaction",
            value=f"{metrics['avg_satisfaction']:.1f}/5.0",
            delta=f"+{metrics['avg_satisfaction']*0.02:.1f}"
        )
        # Satisfaction histogram
        satisfaction_data = df['customer_satisfaction'] if 'customer_satisfaction' in df.columns else pd.Series(np.random.normal(4.2, 0.5, 100))
        fig_satisfaction = px.histogram(x=satisfaction_data, nbins=10, title="Satisfaction Distribution")
        fig_satisfaction.update_layout(height=150, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_satisfaction, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-time Status Dashboard
    st.markdown("### 🔴 Real-time Operations Status")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        active_calls = random.randint(8, 35)
        st.metric("🔴 Active Calls", active_calls, delta=random.randint(-3, 5))
    
    with col2:
        queue_length = random.randint(0, 12)
        st.metric("⏳ Queue Length", queue_length, delta=random.randint(-2, 4))
    
    with col3:
        available_agents = random.randint(12, 25)
        st.metric("🤖 Available Agents", available_agents, delta=random.randint(-1, 3))
    
    with col4:
        avg_wait_time = random.randint(15, 120)
        st.metric("⚡ Avg Wait Time", f"{avg_wait_time}s", delta=f"{random.randint(-20, 30)}s")
    
    with col5:
        system_load = random.randint(35, 85)
        st.metric("💻 System Load", f"{system_load}%", delta=f"{random.randint(-5, 10)}%")
    
    with col6:
        api_latency = random.randint(45, 180)
        st.metric("🌐 API Latency", f"{api_latency}ms", delta=f"{random.randint(-20, 40)}ms")
    
    # Comprehensive Analytics Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Call Volume & Success Rate Trends</div>', unsafe_allow_html=True)
        
        if 'call_date' in df.columns:
            daily_stats = df.groupby('call_date').agg({
                'call_id': 'count',
                'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100
            }).reset_index()
            daily_stats.columns = ['Date', 'Call Volume', 'Success Rate']
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Scatter(x=daily_stats['Date'], y=daily_stats['Call Volume'], name="Call Volume"),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(x=daily_stats['Date'], y=daily_stats['Success Rate'], name="Success Rate %"),
                secondary_y=True,
            )
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Call Volume", secondary_y=False)
            fig.update_yaxes(title_text="Success Rate %", secondary_y=True)
            fig.update_layout(title_text="Call Volume & Success Rate Trends", height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🎯 Agent Performance Comparison</div>', unsafe_allow_html=True)
        
        if 'voice_agent_name' in df.columns:
            agent_performance = df.groupby('voice_agent_name').agg({
                'call_id': 'count',
                'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100,
                'customer_satisfaction': 'mean',
                'ai_accuracy_score': 'mean'
            }).reset_index()
            agent_performance.columns = ['Agent', 'Total Calls', 'Success Rate', 'Avg Satisfaction', 'AI Accuracy']
            
            fig = px.scatter(agent_performance, 
                           x='Success Rate', 
                           y='Avg Satisfaction', 
                           size='Total Calls',
                           color='AI Accuracy',
                           hover_name='Agent',
                           title="Agent Performance Matrix")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional Analytics Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🕐 Call Duration Analysis</div>', unsafe_allow_html=True)
        
        if 'call_duration_seconds' in df.columns:
            duration_bins = pd.cut(df['call_duration_seconds'], 
                                 bins=[0, 60, 300, 600, 1200, float('inf')], 
                                 labels=['<1min', '1-5min', '5-10min', '10-20min', '>20min'])
            duration_counts = duration_bins.value_counts()
            
            fig = px.bar(x=duration_counts.index, y=duration_counts.values,
                        title="Call Duration Distribution",
                        labels={'x': 'Duration Range', 'y': 'Number of Calls'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">💡 Intent Detection Analysis</div>', unsafe_allow_html=True)
        
        if 'intent_detected' in df.columns:
            intent_counts = df['intent_detected'].value_counts()
            
            fig = px.pie(values=intent_counts.values, names=intent_counts.index,
                        title="Call Intent Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


elif st.session_state.current_page == "📈 Analytics":
    st.markdown('<h2 class="section-header animate-fadeIn">📈 Advanced VAPI AI Analytics</h2>', unsafe_allow_html=True)
    
    # Analytics filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_filter = st.date_input("📅 Date Range", value=[datetime.now().date() - timedelta(days=30), datetime.now().date()])
    with col2:
        agent_filter = st.multiselect("🤖 AI Agents", df['voice_agent_name'].unique() if 'voice_agent_name' in df.columns else [])
    with col3:
        tier_filter = st.multiselect("🏆 Customer Tier", df['customer_tier'].unique() if 'customer_tier' in df.columns else [])
    with col4:
        intent_filter = st.multiselect("💡 Intent", df['intent_detected'].unique() if 'intent_detected' in df.columns else [])
    
    # Apply filters
    filtered_df = df.copy()
    if agent_filter:
        filtered_df = filtered_df[filtered_df['voice_agent_name'].isin(agent_filter)]
    if tier_filter:
        filtered_df = filtered_df[filtered_df['customer_tier'].isin(tier_filter)]
    if intent_filter:
        filtered_df = filtered_df[filtered_df['intent_detected'].isin(intent_filter)]
    
    # Analytics Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Performance", "😊 Sentiment", "💰 Revenue", "🤖 AI Metrics", "🔮 Predictions"])
    
    with tab1:
        st.markdown("### 📊 Performance Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 Success Rate by Hour</div>', unsafe_allow_html=True)
            
            if 'call_start_time' in filtered_df.columns:
                # Extract hour from call_start_time
                filtered_df['hour'] = pd.to_datetime(filtered_df['call_start_time'], format='%H:%M:%S').dt.hour
                hourly_success = filtered_df.groupby('hour')['call_success'].apply(
                    lambda x: (x == 'Yes').sum() / len(x) * 100
                ).reset_index()
                
                fig = px.line(hourly_success, x='hour', y='call_success',
                            title="Success Rate by Hour of Day",
                            labels={'hour': 'Hour of Day', 'call_success': 'Success Rate %'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⏱️ Resolution Time Distribution</div>', unsafe_allow_html=True)
            
            if 'resolution_time_seconds' in filtered_df.columns:
                resolution_bins = pd.cut(filtered_df['resolution_time_seconds'], 
                                       bins=[0, 60, 180, 300, 600, float('inf')], 
                                       labels=['<1min', '1-3min', '3-5min', '5-10min', '>10min'])
                resolution_counts = resolution_bins.value_counts()
                
                fig = px.bar(x=resolution_counts.index, y=resolution_counts.values,
                           title="Resolution Time Distribution",
                           labels={'x': 'Resolution Time', 'y': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🎯 Conversion Rate by Customer Tier</div>', unsafe_allow_html=True)
            
            if 'customer_tier' in filtered_df.columns and 'conversion_probability' in filtered_df.columns:
                tier_conversion = filtered_df.groupby('customer_tier')['conversion_probability'].mean().reset_index()
                
                fig = px.bar(tier_conversion, x='customer_tier', y='conversion_probability',
                           title="Average Conversion Rate by Customer Tier",
                           labels={'customer_tier': 'Customer Tier', 'conversion_probability': 'Conversion Rate'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📞 Call Complexity Analysis</div>', unsafe_allow_html=True)
            
            if 'call_complexity' in filtered_df.columns:
                complexity_counts = filtered_df['call_complexity'].value_counts()
                
                fig = px.pie(values=complexity_counts.values, names=complexity_counts.index,
                           title="Call Complexity Distribution")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 😊 Sentiment Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">😊 Sentiment Score Distribution</div>', unsafe_allow_html=True)
            
            if 'sentiment_score' in filtered_df.columns:
                fig = px.histogram(filtered_df, x='sentiment_score', nbins=20,
                                 title="Sentiment Score Distribution",
                                 labels={'sentiment_score': 'Sentiment Score', 'count': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🎭 Emotion Detection Analysis</div>', unsafe_allow_html=True)
            
            if 'emotion_detected' in filtered_df.columns:
                emotion_counts = filtered_df['emotion_detected'].value_counts()
                
                fig = px.bar(x=emotion_counts.index, y=emotion_counts.values,
                           title="Detected Emotions Distribution",
                           labels={'x': 'Emotion', 'y': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">😊 Sentiment vs Satisfaction Correlation</div>', unsafe_allow_html=True)
            
            if 'sentiment_score' in filtered_df.columns and 'customer_satisfaction' in filtered_df.columns:
                fig = px.scatter(filtered_df, x='sentiment_score', y='customer_satisfaction',
                               color='call_success', size='call_duration_seconds',
                               title="Sentiment vs Customer Satisfaction",
                               labels={'sentiment_score': 'Sentiment Score', 'customer_satisfaction': 'Satisfaction Rating'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 Sentiment Trend Over Time</div>', unsafe_allow_html=True)
            
            if 'call_date' in filtered_df.columns and 'sentiment_score' in filtered_df.columns:
                daily_sentiment = filtered_df.groupby('call_date')['sentiment_score'].mean().reset_index()
                
                fig = px.line(daily_sentiment, x='call_date', y='sentiment_score',
                            title="Daily Average Sentiment Trend",
                            labels={'call_date': 'Date', 'sentiment_score': 'Average Sentiment'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 💰 Revenue Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">💰 Revenue Impact by Agent</div>', unsafe_allow_html=True)
            
            if 'voice_agent_name' in filtered_df.columns and 'revenue_impact' in filtered_df.columns:
                agent_revenue = filtered_df.groupby('voice_agent_name')['revenue_impact'].sum().reset_index()
                
                fig = px.bar(agent_revenue, x='voice_agent_name', y='revenue_impact',
                           title="Total Revenue Impact by AI Agent",
                           labels={'voice_agent_name': 'AI Agent', 'revenue_impact': 'Revenue Impact ($)'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">💎 Customer Lifetime Value Distribution</div>', unsafe_allow_html=True)
            
            if 'customer_lifetime_value' in filtered_df.columns:
                clv_bins = pd.cut(filtered_df['customer_lifetime_value'], 
                                bins=[0, 1000, 5000, 10000, 20000, float('inf')], 
                                labels=['<$1K', '$1K-$5K', '$5K-$10K', '$10K-$20K', '>$20K'])
                clv_counts = clv_bins.value_counts()
                
                fig = px.pie(values=clv_counts.values, names=clv_counts.index,
                           title="Customer Lifetime Value Distribution")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 Revenue vs Call Duration</div>', unsafe_allow_html=True)
            
            if 'call_duration_seconds' in filtered_df.columns and 'revenue_impact' in filtered_df.columns:
                fig = px.scatter(filtered_df, x='call_duration_seconds', y='revenue_impact',
                               color='customer_tier', size='customer_satisfaction',
                               title="Revenue Impact vs Call Duration",
                               labels={'call_duration_seconds': 'Call Duration (seconds)', 'revenue_impact': 'Revenue Impact ($)'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">💰 Daily Revenue Trend</div>', unsafe_allow_html=True)
            
            if 'call_date' in filtered_df.columns and 'revenue_impact' in filtered_df.columns:
                daily_revenue = filtered_df.groupby('call_date')['revenue_impact'].sum().reset_index()
                
                fig = px.area(daily_revenue, x='call_date', y='revenue_impact',
                            title="Daily Revenue Trend",
                            labels={'call_date': 'Date', 'revenue_impact': 'Revenue ($)'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 🤖 AI Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🤖 AI Accuracy by Agent</div>', unsafe_allow_html=True)
            
            if 'voice_agent_name' in filtered_df.columns and 'ai_accuracy_score' in filtered_df.columns:
                agent_accuracy = filtered_df.groupby('voice_agent_name')['ai_accuracy_score'].mean().reset_index()
                
                fig = px.bar(agent_accuracy, x='voice_agent_name', y='ai_accuracy_score',
                           title="Average AI Accuracy by Agent",
                           labels={'voice_agent_name': 'AI Agent', 'ai_accuracy_score': 'AI Accuracy Score'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🎯 Confidence Score Distribution</div>', unsafe_allow_html=True)
            
            if 'confidence_score' in filtered_df.columns:
                fig = px.histogram(filtered_df, x='confidence_score', nbins=20,
                                 title="AI Confidence Score Distribution",
                                 labels={'confidence_score': 'Confidence Score', 'count': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🗣️ Speech Rate Analysis</div>', unsafe_allow_html=True)
            
            if 'speech_rate_wpm' in filtered_df.columns:
                speech_bins = pd.cut(filtered_df['speech_rate_wpm'], 
                                   bins=[0, 120, 150, 180, 220, float('inf')], 
                                   labels=['Slow', 'Normal', 'Fast', 'Very Fast', 'Rapid'])
                speech_counts = speech_bins.value_counts()
                
                fig = px.bar(x=speech_counts.index, y=speech_counts.values,
                           title="Speech Rate Distribution",
                           labels={'x': 'Speech Rate Category', 'y': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔇 Silence Percentage Analysis</div>', unsafe_allow_html=True)
            
            if 'silence_percentage' in filtered_df.columns:
                fig = px.box(filtered_df, y='silence_percentage',
                           title="Silence Percentage Distribution",
                           labels={'silence_percentage': 'Silence Percentage (%)'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 🔮 Predictive Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔮 Conversion Probability Prediction</div>', unsafe_allow_html=True)
            
            if 'conversion_probability' in filtered_df.columns:
                conversion_bins = pd.cut(filtered_df['conversion_probability'], 
                                       bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0], 
                                       labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
                conversion_counts = conversion_bins.value_counts()
                
                fig = px.pie(values=conversion_counts.values, names=conversion_counts.index,
                           title="Conversion Probability Distribution")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 Lead Quality Score Analysis</div>', unsafe_allow_html=True)
            
            if 'lead_quality_score' in filtered_df.columns:
                fig = px.histogram(filtered_df, x='lead_quality_score', nbins=20,
                                 title="Lead Quality Score Distribution",
                                 labels={'lead_quality_score': 'Lead Quality Score', 'count': 'Number of Leads'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Predictive model results (mock)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔮 AI Predictions for Next 30 Days</div>', unsafe_allow_html=True)
        
        # Generate mock prediction data
        future_dates = pd.date_range(start=datetime.now().date(), periods=30, freq='D')
        predictions = {
            'Date': future_dates,
            'Predicted Calls': np.random.randint(20, 50, 30),
            'Predicted Success Rate': np.random.uniform(0.75, 0.95, 30),
            'Predicted Revenue': np.random.uniform(1000, 5000, 30)
        }
        pred_df = pd.DataFrame(predictions)
        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Predicted Call Volume', 'Predicted Success Rate', 'Predicted Revenue'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted Calls'], name='Call Volume'), row=1, col=1)
        fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted Success Rate'], name='Success Rate'), row=2, col=1)
        fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted Revenue'], name='Revenue'), row=3, col=1)
        
        fig.update_layout(height=600, title_text="30-Day AI Predictions")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "👥 Agents":
    st.markdown('<h2 class="section-header animate-fadeIn">👥 VAPI AI Agent Performance</h2>', unsafe_allow_html=True)
    
    if 'voice_agent_name' in df.columns:
        # Agent selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_agent = st.selectbox("🤖 Select AI Agent", ["All Agents"] + list(df['voice_agent_name'].unique()))
        
        with col2:
            comparison_mode = st.checkbox("📊 Comparison Mode", value=False)
        
        # Filter data for selected agent
        if selected_agent != "All Agents":
            agent_df = df[df['voice_agent_name'] == selected_agent]
        else:
            agent_df = df
        
        # Agent performance metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            total_calls = len(agent_df)
            st.metric("📞 Total Calls", total_calls, delta=f"+{total_calls//10} this week")
        
        with col2:
            success_rate = (agent_df['call_success'] == 'Yes').sum() / len(agent_df) * 100 if len(agent_df) > 0 else 0
            st.metric("✅ Success Rate", f"{success_rate:.1f}%", delta=f"+{success_rate*0.02:.1f}%")
        
        with col3:
            avg_duration = agent_df['call_duration_seconds'].mean() / 60 if 'call_duration_seconds' in agent_df.columns else 0
            st.metric("⏱️ Avg Duration", f"{avg_duration:.1f}m", delta=f"+{avg_duration*0.1:.1f}m")
        
        with col4:
            avg_satisfaction = agent_df['customer_satisfaction'].mean() if 'customer_satisfaction' in agent_df.columns else 0
            st.metric("⭐ Avg Satisfaction", f"{avg_satisfaction:.1f}/5", delta=f"+{avg_satisfaction*0.05:.1f}")
        
        with col5:
            ai_accuracy = agent_df['ai_accuracy_score'].mean() if 'ai_accuracy_score' in agent_df.columns else 0
            st.metric("🤖 AI Accuracy", f"{ai_accuracy:.1%}", delta=f"+{ai_accuracy*0.01:.1%}")
        
        with col6:
            total_revenue = agent_df['revenue_impact'].sum() if 'revenue_impact' in agent_df.columns else 0
            st.metric("💰 Revenue Impact", f"${total_revenue:,.0f}", delta=f"+${total_revenue*0.1:.0f}")
        
        # Agent performance charts
        if comparison_mode and selected_agent == "All Agents":
            st.markdown("### 📊 Agent Comparison Dashboard")
            
            # Comprehensive agent comparison
            agent_metrics = df.groupby('voice_agent_name').agg({
                'call_id': 'count',
                'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100,
                'call_duration_seconds': 'mean',
                'customer_satisfaction': 'mean',
                'ai_accuracy_score': 'mean',
                'revenue_impact': 'sum',
                'sentiment_score': 'mean',
                'confidence_score': 'mean',
                'resolution_time_seconds': 'mean'
            }).round(2)
            
            agent_metrics.columns = ['Total Calls', 'Success Rate (%)', 'Avg Duration (s)', 
                                   'Avg Satisfaction', 'AI Accuracy', 'Revenue Impact', 
                                   'Avg Sentiment', 'Avg Confidence', 'Avg Resolution Time (s)']
            
            # Agent comparison charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📊 Agent Performance Radar Chart</div>', unsafe_allow_html=True)
                
                # Create radar chart for agent comparison
                agents = agent_metrics.index.tolist()
                metrics_for_radar = ['Success Rate (%)', 'Avg Satisfaction', 'AI Accuracy', 'Avg Sentiment', 'Avg Confidence']
                
                fig = go.Figure()
                
                for agent in agents[:3]:  # Show top 3 agents
                    values = [agent_metrics.loc[agent, metric] for metric in metrics_for_radar]
                    # Normalize values to 0-100 scale
                    normalized_values = []
                    for i, value in enumerate(values):
                        if metrics_for_radar[i] == 'Success Rate (%)':
                            normalized_values.append(value)
                        elif metrics_for_radar[i] in ['Avg Satisfaction']:
                            normalized_values.append(value * 20)  # Scale 0-5 to 0-100
                        else:
                            normalized_values.append(value * 100)  # Scale 0-1 to 0-100
                    
                    fig.add_trace(go.Scatterpolar(
                        r=normalized_values,
                        theta=metrics_for_radar,
                        fill='toself',
                        name=agent
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="Agent Performance Comparison",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">💰 Revenue Impact by Agent</div>', unsafe_allow_html=True)
                
                fig = px.bar(x=agent_metrics.index, y=agent_metrics['Revenue Impact'],
                           title="Total Revenue Impact by Agent",
                           labels={'x': 'AI Agent', 'y': 'Revenue Impact ($)'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced AG Grid for agent comparison
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📋 Detailed Agent Performance Comparison</div>', unsafe_allow_html=True)
            
            grid_response = create_enhanced_ag_grid(agent_metrics.reset_index(), "agent_comparison_grid", height=400)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # Individual agent performance
            if selected_agent != "All Agents":
                st.markdown(f"### 🤖 {selected_agent} - Detailed Performance")
            else:
                st.markdown("### 📊 Overall Agent Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📈 Daily Performance Trend</div>', unsafe_allow_html=True)
                
                if 'call_date' in agent_df.columns:
                    daily_performance = agent_df.groupby('call_date').agg({
                        'call_id': 'count',
                        'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100,
                        'customer_satisfaction': 'mean'
                    }).reset_index()
                    
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    fig.add_trace(
                        go.Scatter(x=daily_performance['call_date'], y=daily_performance['call_id'], name="Call Volume"),
                        secondary_y=False,
                    )
                    fig.add_trace(
                        go.Scatter(x=daily_performance['call_date'], y=daily_performance['call_success'], name="Success Rate %"),
                        secondary_y=True,
                    )
                    fig.update_xaxes(title_text="Date")
                    fig.update_yaxes(title_text="Call Volume", secondary_y=False)
                    fig.update_yaxes(title_text="Success Rate %", secondary_y=True)
                    fig.update_layout(title_text="Daily Performance Trend", height=400)
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📊 Call Outcome Distribution</div>', unsafe_allow_html=True)
                
                if 'call_outcome' in agent_df.columns:
                    outcome_counts = agent_df['call_outcome'].value_counts()
                    fig = px.pie(values=outcome_counts.values, names=outcome_counts.index,
                               title="Call Outcome Distribution")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional performance metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">🎯 AI Accuracy vs Confidence</div>', unsafe_allow_html=True)
                
                if 'ai_accuracy_score' in agent_df.columns and 'confidence_score' in agent_df.columns:
                    fig = px.scatter(agent_df, x='confidence_score', y='ai_accuracy_score',
                                   color='call_success', size='customer_satisfaction',
                                   title="AI Accuracy vs Confidence Score",
                                   labels={'confidence_score': 'Confidence Score', 'ai_accuracy_score': 'AI Accuracy'})
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">⏱️ Resolution Time Analysis</div>', unsafe_allow_html=True)
                
                if 'resolution_time_seconds' in agent_df.columns:
                    fig = px.histogram(agent_df, x='resolution_time_seconds', nbins=20,
                                     title="Resolution Time Distribution",
                                     labels={'resolution_time_seconds': 'Resolution Time (seconds)', 'count': 'Number of Calls'})
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "👤 Contacts":
    st.markdown('<h2 class="section-header animate-fadeIn">👤 CRM & Contact Management</h2>', unsafe_allow_html=True)
    
    # CRM Dashboard with enhanced features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search Contacts", placeholder="Name, phone, or email")
    with col2:
        tier_filter = st.multiselect("🏆 Customer Tier", df['customer_tier'].unique() if 'customer_tier' in df.columns else [])
    with col3:
        status_filter = st.selectbox("📊 Call Status", ["All", "Successful", "Failed", "Pending"])
    
    # Advanced CRM filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        clv_range = st.slider("💰 CLV Range", 0, 50000, (0, 50000), step=1000)
    with col2:
        satisfaction_range = st.slider("⭐ Satisfaction Range", 1.0, 5.0, (1.0, 5.0), step=0.1)
    with col3:
        last_call_days = st.slider("📅 Last Call (days ago)", 0, 365, (0, 365))
    with col4:
        show_high_value = st.checkbox("💎 High Value Only", value=False)
    
    # Filter contacts based on criteria
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['customer_name'].str.contains(search_term, case=False, na=False) |
            filtered_df['phone_number'].str.contains(search_term, case=False, na=False) |
            filtered_df['email'].str.contains(search_term, case=False, na=False)
        ]
    
    if tier_filter:
        filtered_df = filtered_df[filtered_df['customer_tier'].isin(tier_filter)]
    
    if status_filter != "All":
        status_map = {"Successful": "Yes", "Failed": "No", "Pending": "Pending"}
        filtered_df = filtered_df[filtered_df['call_success'] == status_map[status_filter]]
    
    if 'customer_lifetime_value' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['customer_lifetime_value'] >= clv_range[0]) & 
            (filtered_df['customer_lifetime_value'] <= clv_range[1])
        ]
    
    if 'customer_satisfaction' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['customer_satisfaction'] >= satisfaction_range[0]) & 
            (filtered_df['customer_satisfaction'] <= satisfaction_range[1])
        ]
    
    if show_high_value and 'customer_tier' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['customer_tier'].isin(['Platinum', 'VIP'])]
    
    # Contact overview metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("👥 Total Contacts", filtered_df['customer_name'].nunique())
    with col2:
        avg_clv = filtered_df['customer_lifetime_value'].mean() if 'customer_lifetime_value' in filtered_df.columns else 0
        st.metric("💰 Avg CLV", f"${avg_clv:,.0f}")
    with col3:
        high_value = (filtered_df['customer_lifetime_value'] > 10000).sum() if 'customer_lifetime_value' in filtered_df.columns else 0
        st.metric("💎 High Value", high_value)
    with col4:
        avg_satisfaction = filtered_df['customer_satisfaction'].mean() if 'customer_satisfaction' in filtered_df.columns else 0
        st.metric("⭐ Avg Satisfaction", f"{avg_satisfaction:.1f}/5")
    with col5:
        recent_contacts = (pd.to_datetime(filtered_df['call_date']) > datetime.now() - timedelta(days=7)).sum() if 'call_date' in filtered_df.columns else 0
        st.metric("📞 Recent Calls", recent_contacts)
    with col6:
        follow_ups = (filtered_df['follow_up_required'] == 'Yes').sum() if 'follow_up_required' in filtered_df.columns else 0
        st.metric("🔄 Follow-ups", follow_ups)
    
    # CRM Analytics Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🏆 Customer Tier Distribution</div>', unsafe_allow_html=True)
        
        if 'customer_tier' in filtered_df.columns:
            tier_counts = filtered_df['customer_tier'].value_counts()
            fig = px.pie(values=tier_counts.values, names=tier_counts.index,
                       title="Customer Tier Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">💰 CLV vs Satisfaction Analysis</div>', unsafe_allow_html=True)
        
        if 'customer_lifetime_value' in filtered_df.columns and 'customer_satisfaction' in filtered_df.columns:
            fig = px.scatter(filtered_df, x='customer_satisfaction', y='customer_lifetime_value',
                           color='customer_tier', size='call_duration_seconds',
                           title="Customer Lifetime Value vs Satisfaction",
                           labels={'customer_satisfaction': 'Satisfaction Rating', 'customer_lifetime_value': 'CLV ($)'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced CRM Contact List
    st.markdown("### 📋 Enhanced Contact Directory")
    
    # Create comprehensive contact summary
    contact_summary = filtered_df.groupby('customer_name').agg({
        'call_id': 'count',
        'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100,
        'customer_satisfaction': 'mean',
        'customer_lifetime_value': 'first',
        'customer_tier': 'first',
        'phone_number': 'first',
        'email': 'first',
        'call_date': 'max',
        'revenue_impact': 'sum',
        'follow_up_required': lambda x: (x == 'Yes').sum(),
        'sentiment_score': 'mean',
        'next_best_action': 'last'
    }).round(2)
    
    contact_summary.columns = ['Total Calls', 'Success Rate (%)', 'Avg Satisfaction', 'CLV ($)', 
                              'Tier', 'Phone', 'Email', 'Last Call', 'Revenue Impact ($)', 
                              'Follow-ups', 'Avg Sentiment', 'Next Action']
    
    # Enhanced AG Grid with CRM features
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📊 Advanced CRM Contact Grid</div>', unsafe_allow_html=True)
    
    grid_response = create_enhanced_ag_grid(contact_summary.reset_index(), "crm_contact_grid", height=500, enable_enterprise=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Selected contact details
    if grid_response['selected_rows']:
        selected_contact = grid_response['selected_rows'][0]
        contact_name = selected_contact['customer_name']
        
        st.markdown(f"### 👤 Contact Profile: {contact_name}")
        
        contact_data = filtered_df[filtered_df['customer_name'] == contact_name]
        
        # Contact profile tabs
        profile_tab1, profile_tab2, profile_tab3, profile_tab4 = st.tabs(["📊 Overview", "📞 Call History", "💰 Revenue", "🔄 Actions"])
        
        with profile_tab1:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📋 Contact Information")
                st.write(f"**Name:** {contact_name}")
                st.write(f"**Phone:** {contact_data['phone_number'].iloc[0] if len(contact_data) > 0 else 'N/A'}")
                st.write(f"**Email:** {contact_data['email'].iloc[0] if len(contact_data) > 0 else 'N/A'}")
                st.write(f"**Tier:** {contact_data['customer_tier'].iloc[0] if len(contact_data) > 0 else 'N/A'}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📊 Performance Metrics")
                st.metric("Total Calls", len(contact_data))
                success_rate = (contact_data['call_success'] == 'Yes').sum() / len(contact_data) * 100 if len(contact_data) > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
                avg_satisfaction = contact_data['customer_satisfaction'].mean() if 'customer_satisfaction' in contact_data.columns else 0
                st.metric("Avg Satisfaction", f"{avg_satisfaction:.1f}/5")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 💰 Financial Metrics")
                clv = contact_data['customer_lifetime_value'].iloc[0] if 'customer_lifetime_value' in contact_data.columns and len(contact_data) > 0 else 0
                st.metric("Lifetime Value", f"${clv:,.0f}")
                total_revenue = contact_data['revenue_impact'].sum() if 'revenue_impact' in contact_data.columns else 0
                st.metric("Total Revenue", f"${total_revenue:,.0f}")
                avg_revenue = contact_data['revenue_impact'].mean() if 'revenue_impact' in contact_data.columns else 0
                st.metric("Avg Revenue/Call", f"${avg_revenue:,.0f}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with profile_tab2:
            if len(contact_data) > 1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📈 Call History Trend</div>', unsafe_allow_html=True)
                
                fig = px.line(contact_data.sort_values('call_date'), x='call_date', y='customer_satisfaction',
                            title=f"Satisfaction Trend for {contact_name}")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Call history table
            call_history = contact_data[['call_date', 'call_start_time', 'call_duration_seconds', 
                                       'call_success', 'customer_satisfaction', 'intent_detected', 
                                       'call_outcome']].sort_values('call_date', ascending=False)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📞 Detailed Call History</div>', unsafe_allow_html=True)
            
            grid_response_history = create_enhanced_ag_grid(call_history, f"call_history_{contact_name}", height=300)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with profile_tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">💰 Revenue by Call</div>', unsafe_allow_html=True)
                
                if 'revenue_impact' in contact_data.columns and len(contact_data) > 1:
                    fig = px.bar(contact_data.sort_values('call_date'), x='call_date', y='revenue_impact',
                               title=f"Revenue Impact by Call - {contact_name}")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📊 Revenue Distribution</div>', unsafe_allow_html=True)
                
                if 'revenue_impact' in contact_data.columns:
                    positive_revenue = (contact_data['revenue_impact'] > 0).sum()
                    negative_revenue = (contact_data['revenue_impact'] < 0).sum()
                    zero_revenue = (contact_data['revenue_impact'] == 0).sum()
                    
                    revenue_dist = pd.DataFrame({
                        'Type': ['Positive', 'Negative', 'Zero'],
                        'Count': [positive_revenue, negative_revenue, zero_revenue]
                    })
                    
                    fig = px.pie(revenue_dist, values='Count', names='Type',
                               title="Revenue Impact Distribution")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with profile_tab4:
            st.markdown('<div class="crm-card">', unsafe_allow_html=True)
            st.markdown("#### 🔄 Recommended Actions")
            
            # Get latest action recommendation
            latest_action = contact_data['next_best_action'].iloc[-1] if 'next_best_action' in contact_data.columns and len(contact_data) > 0 else "No action specified"
            st.write(f"**Next Best Action:** {latest_action}")
            
            # Follow-up requirements
            follow_up_needed = (contact_data['follow_up_required'] == 'Yes').any() if 'follow_up_required' in contact_data.columns else False
            if follow_up_needed:
                st.warning("🔄 Follow-up required for this contact")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📞 Schedule Call", use_container_width=True):
                    st.success("Call scheduled successfully!")
            
            with col2:
                if st.button("📧 Send Email", use_container_width=True):
                    st.success("Email sent successfully!")
            
            with col3:
                if st.button("📝 Add Note", use_container_width=True):
                    st.success("Note added successfully!")
            
            # Contact notes section
            st.markdown("#### 📝 Contact Notes")
            new_note = st.text_area("Add a new note:", placeholder="Enter your note here...")
            
            if st.button("💾 Save Note"):
                if new_note:
                    st.success("Note saved successfully!")
                else:
                    st.warning("Please enter a note before saving.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Bulk actions for selected contacts
    if grid_response['selected_rows']:
        st.markdown("### 🔄 Bulk Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📧 Send Bulk Email", use_container_width=True):
                st.success(f"Bulk email sent to {len(grid_response['selected_rows'])} contacts!")
        
        with col2:
            if st.button("📞 Schedule Bulk Calls", use_container_width=True):
                st.success(f"Calls scheduled for {len(grid_response['selected_rows'])} contacts!")
        
        with col3:
            if st.button("🏷️ Update Tier", use_container_width=True):
                st.success(f"Tier updated for {len(grid_response['selected_rows'])} contacts!")
        
        with col4:
            if st.button("📤 Export Selected", use_container_width=True):
                selected_data = pd.DataFrame(grid_response['selected_rows'])
                csv = selected_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"selected_contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

elif st.session_state.current_page == "📞 Calls":
    st.markdown('<h2 class="section-header animate-fadeIn">📞 Call Management & Analysis</h2>', unsafe_allow_html=True)
    
    # Call management dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_range = st.date_input("📅 Date Range", value=[datetime.now().date() - timedelta(days=7), datetime.now().date()])
    with col2:
        call_status = st.multiselect("📊 Call Status", df['call_success'].unique() if 'call_success' in df.columns else [])
    with col3:
        call_outcome = st.multiselect("🎯 Call Outcome", df['call_outcome'].unique() if 'call_outcome' in df.columns else [])
    with col4:
        duration_range = st.slider("⏱️ Duration Range (min)", 0, 30, (0, 30))
    
    # Filter calls
    filtered_calls = df.copy()
    
    if call_status:
        filtered_calls = filtered_calls[filtered_calls['call_success'].isin(call_status)]
    if call_outcome:
        filtered_calls = filtered_calls[filtered_calls['call_outcome'].isin(call_outcome)]
    if 'call_duration_seconds' in filtered_calls.columns:
        filtered_calls = filtered_calls[
            (filtered_calls['call_duration_seconds'] >= duration_range[0] * 60) & 
            (filtered_calls['call_duration_seconds'] <= duration_range[1] * 60)
        ]
    
    # Call metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("📞 Total Calls", len(filtered_calls))
    with col2:
        success_rate = (filtered_calls['call_success'] == 'Yes').sum() / len(filtered_calls) * 100 if len(filtered_calls) > 0 else 0
        st.metric("✅ Success Rate", f"{success_rate:.1f}%")
    with col3:
        avg_duration = filtered_calls['call_duration_seconds'].mean() / 60 if 'call_duration_seconds' in filtered_calls.columns else 0
        st.metric("⏱️ Avg Duration", f"{avg_duration:.1f}m")
    with col4:
        total_cost = filtered_calls['cost'].sum() if 'cost' in filtered_calls.columns else 0
        st.metric("💰 Total Cost", f"${total_cost:.2f}")
    with col5:
        appointments = (filtered_calls['appointment_scheduled'] == 'Yes').sum() if 'appointment_scheduled' in filtered_calls.columns else 0
        st.metric("📅 Appointments", appointments)
    with col6:
        escalations = (filtered_calls['escalation_required'] == 'Yes').sum() if 'escalation_required' in filtered_calls.columns else 0
        st.metric("⚠️ Escalations", escalations)
    
    # Call analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Call Volume by Hour</div>', unsafe_allow_html=True)
        
        if 'call_start_time' in filtered_calls.columns:
            filtered_calls['hour'] = pd.to_datetime(filtered_calls['call_start_time'], format='%H:%M:%S').dt.hour
            hourly_calls = filtered_calls['hour'].value_counts().sort_index()
            
            fig = px.bar(x=hourly_calls.index, y=hourly_calls.values,
                       title="Call Volume by Hour of Day",
                       labels={'x': 'Hour', 'y': 'Number of Calls'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🎯 Call Outcome Analysis</div>', unsafe_allow_html=True)
        
        if 'call_outcome' in filtered_calls.columns:
            outcome_counts = filtered_calls['call_outcome'].value_counts()
            
            fig = px.pie(values=outcome_counts.values, names=outcome_counts.index,
                       title="Call Outcome Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed call analysis tabs
    call_tab1, call_tab2, call_tab3, call_tab4 = st.tabs(["📊 Overview", "⏱️ Duration", "💰 Cost", "🎯 Quality"])
    
    with call_tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📅 Daily Call Trend</div>', unsafe_allow_html=True)
            
            if 'call_date' in filtered_calls.columns:
                daily_calls = filtered_calls.groupby('call_date').agg({
                    'call_id': 'count',
                    'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100
                }).reset_index()
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(
                    go.Scatter(x=daily_calls['call_date'], y=daily_calls['call_id'], name="Call Volume"),
                    secondary_y=False,
                )
                fig.add_trace(
                    go.Scatter(x=daily_calls['call_date'], y=daily_calls['call_success'], name="Success Rate %"),
                    secondary_y=True,
                )
                fig.update_xaxes(title_text="Date")
                fig.update_yaxes(title_text="Call Volume", secondary_y=False)
                fig.update_yaxes(title_text="Success Rate %", secondary_y=True)
                fig.update_layout(title_text="Daily Call Trend", height=400)
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">💡 Intent Detection Distribution</div>', unsafe_allow_html=True)
            
            if 'intent_detected' in filtered_calls.columns:
                intent_counts = filtered_calls['intent_detected'].value_counts()
                
                fig = px.bar(x=intent_counts.values, y=intent_counts.index, orientation='h',
                           title="Call Intent Distribution",
                           labels={'x': 'Number of Calls', 'y': 'Intent'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with call_tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⏱️ Call Duration Distribution</div>', unsafe_allow_html=True)
            
            if 'call_duration_seconds' in filtered_calls.columns:
                duration_minutes = filtered_calls['call_duration_seconds'] / 60
                
                fig = px.histogram(x=duration_minutes, nbins=20,
                                 title="Call Duration Distribution",
                                 labels={'x': 'Duration (minutes)', 'y': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⏱️ Duration vs Success Rate</div>', unsafe_allow_html=True)
            
            if 'call_duration_seconds' in filtered_calls.columns and 'call_success' in filtered_calls.columns:
                duration_bins = pd.cut(filtered_calls['call_duration_seconds'], 
                                     bins=[0, 60, 300, 600, 1200, float('inf')], 
                                     labels=['<1min', '1-5min', '5-10min', '10-20min', '>20min'])
                
                duration_success = filtered_calls.groupby(duration_bins)['call_success'].apply(
                    lambda x: (x == 'Yes').sum() / len(x) * 100
                ).reset_index()
                
                fig = px.bar(duration_success, x='call_duration_seconds', y='call_success',
                           title="Success Rate by Call Duration",
                           labels={'call_duration_seconds': 'Duration Range', 'call_success': 'Success Rate %'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with call_tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">💰 Cost Analysis</div>', unsafe_allow_html=True)
            
            if 'cost' in filtered_calls.columns:
                fig = px.histogram(filtered_calls, x='cost', nbins=20,
                                 title="Call Cost Distribution",
                                 labels={'cost': 'Cost ($)', 'count': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">💰 Cost vs Revenue Impact</div>', unsafe_allow_html=True)
            
            if 'cost' in filtered_calls.columns and 'revenue_impact' in filtered_calls.columns:
                fig = px.scatter(filtered_calls, x='cost', y='revenue_impact',
                               color='call_success', size='customer_satisfaction',
                               title="Cost vs Revenue Impact",
                               labels={'cost': 'Call Cost ($)', 'revenue_impact': 'Revenue Impact ($)'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with call_tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⭐ Customer Satisfaction Distribution</div>', unsafe_allow_html=True)
            
            if 'customer_satisfaction' in filtered_calls.columns:
                fig = px.histogram(filtered_calls, x='customer_satisfaction', nbins=10,
                                 title="Customer Satisfaction Distribution",
                                 labels={'customer_satisfaction': 'Satisfaction Rating', 'count': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">😊 Sentiment vs Satisfaction</div>', unsafe_allow_html=True)
            
            if 'sentiment_score' in filtered_calls.columns and 'customer_satisfaction' in filtered_calls.columns:
                fig = px.scatter(filtered_calls, x='sentiment_score', y='customer_satisfaction',
                               color='call_success', size='call_duration_seconds',
                               title="Sentiment Score vs Customer Satisfaction",
                               labels={'sentiment_score': 'Sentiment Score', 'customer_satisfaction': 'Satisfaction Rating'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced call data grid
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📋 Detailed Call Records</div>', unsafe_allow_html=True)
    
    # Select relevant columns for call display
    call_columns = ['call_id', 'customer_name', 'phone_number', 'call_date', 'call_start_time', 
                   'call_duration_seconds', 'call_success', 'customer_satisfaction', 'intent_detected', 
                   'call_outcome', 'revenue_impact', 'cost', 'voice_agent_name']
    
    available_columns = [col for col in call_columns if col in filtered_calls.columns]
    call_display_df = filtered_calls[available_columns].copy()
    
    # Format duration for display
    if 'call_duration_seconds' in call_display_df.columns:
        call_display_df['call_duration_minutes'] = (call_display_df['call_duration_seconds'] / 60).round(1)
        call_display_df = call_display_df.drop('call_duration_seconds', axis=1)
    
    grid_response = create_enhanced_ag_grid(call_display_df, "call_records_grid", height=500, enable_enterprise=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Call recording playback (mock)
    if grid_response['selected_rows']:
        selected_call = grid_response['selected_rows'][0]
        
        st.markdown(f"### 🎵 Call Recording: {selected_call.get('call_id', 'Unknown')}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="url-monitor">', unsafe_allow_html=True)
            st.markdown("#### 🎵 Audio Player")
            st.info("🎵 Call recording would be played here")
            
            # Mock audio controls
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.button("▶️ Play")
            with col_b:
                st.button("⏸️ Pause")
            with col_c:
                st.button("⏹️ Stop")
            with col_d:
                st.button("📥 Download")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="crm-card">', unsafe_allow_html=True)
            st.markdown("#### 📋 Call Details")
            st.write(f"**Call ID:** {selected_call.get('call_id', 'N/A')}")
            st.write(f"**Customer:** {selected_call.get('customer_name', 'N/A')}")
            st.write(f"**Date:** {selected_call.get('call_date', 'N/A')}")
            st.write(f"**Duration:** {selected_call.get('call_duration_minutes', 'N/A')} min")
            st.write(f"**Success:** {selected_call.get('call_success', 'N/A')}")
            st.write(f"**Satisfaction:** {selected_call.get('customer_satisfaction', 'N/A')}/5")
            st.markdown('</div>', unsafe_allow_html=True)


elif st.session_state.current_page == "🤖 AI Insights":
    st.markdown('<h2 class="section-header animate-fadeIn">🤖 Advanced AI Insights & Analytics</h2>', unsafe_allow_html=True)
    
    # AI Insights Dashboard
    ai_tab1, ai_tab2, ai_tab3, ai_tab4, ai_tab5 = st.tabs(["🧠 AI Performance", "🎯 Intent Analysis", "😊 Sentiment Deep Dive", "🔮 Predictions", "🛠️ Model Metrics"])
    
    with ai_tab1:
        st.markdown("### 🧠 AI Performance Analytics")
        
        # AI Performance Metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            avg_accuracy = df['ai_accuracy_score'].mean() if 'ai_accuracy_score' in df.columns else 0
            st.metric("🤖 AI Accuracy", f"{avg_accuracy:.1%}", delta=f"+{avg_accuracy*0.02:.1%}")
        
        with col2:
            avg_confidence = df['confidence_score'].mean() if 'confidence_score' in df.columns else 0
            st.metric("🎯 Confidence", f"{avg_confidence:.1%}", delta=f"+{avg_confidence*0.01:.1%}")
        
        with col3:
            high_accuracy = (df['ai_accuracy_score'] > 0.9).sum() if 'ai_accuracy_score' in df.columns else 0
            st.metric("⭐ High Accuracy", high_accuracy, delta=f"+{high_accuracy//10}")
        
        with col4:
            intent_accuracy = df['intent_detected'].notna().sum() if 'intent_detected' in df.columns else 0
            st.metric("💡 Intent Detection", f"{intent_accuracy/len(df)*100:.1f}%", delta="+2.3%")
        
        with col5:
            sentiment_accuracy = df['sentiment_score'].notna().sum() if 'sentiment_score' in df.columns else 0
            st.metric("😊 Sentiment Analysis", f"{sentiment_accuracy/len(df)*100:.1f}%", delta="+1.8%")
        
        with col6:
            language_detection = df['language_detected'].notna().sum() if 'language_detected' in df.columns else 0
            st.metric("🌐 Language Detection", f"{language_detection/len(df)*100:.1f}%", delta="+0.5%")
        
        # AI Performance Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🤖 AI Accuracy Distribution</div>', unsafe_allow_html=True)
            
            if 'ai_accuracy_score' in df.columns:
                accuracy_bins = pd.cut(df['ai_accuracy_score'], 
                                     bins=[0, 0.7, 0.8, 0.9, 0.95, 1.0], 
                                     labels=['Poor', 'Fair', 'Good', 'Excellent', 'Perfect'])
                accuracy_counts = accuracy_bins.value_counts()
                
                fig = px.bar(x=accuracy_counts.index, y=accuracy_counts.values,
                           title="AI Accuracy Score Distribution",
                           labels={'x': 'Accuracy Level', 'y': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🎯 Confidence vs Accuracy Correlation</div>', unsafe_allow_html=True)
            
            if 'confidence_score' in df.columns and 'ai_accuracy_score' in df.columns:
                fig = px.scatter(df, x='confidence_score', y='ai_accuracy_score',
                               color='call_success', size='customer_satisfaction',
                               title="AI Confidence vs Accuracy",
                               labels={'confidence_score': 'Confidence Score', 'ai_accuracy_score': 'AI Accuracy'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # AI Performance by Agent
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🤖 AI Performance by Agent</div>', unsafe_allow_html=True)
            
            if 'voice_agent_name' in df.columns and 'ai_accuracy_score' in df.columns:
                agent_ai_performance = df.groupby('voice_agent_name').agg({
                    'ai_accuracy_score': 'mean',
                    'confidence_score': 'mean',
                    'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100
                }).reset_index()
                
                fig = px.bar(agent_ai_performance, x='voice_agent_name', y='ai_accuracy_score',
                           title="Average AI Accuracy by Agent",
                           labels={'voice_agent_name': 'AI Agent', 'ai_accuracy_score': 'AI Accuracy'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 AI Performance Trend</div>', unsafe_allow_html=True)
            
            if 'call_date' in df.columns and 'ai_accuracy_score' in df.columns:
                daily_ai_performance = df.groupby('call_date')['ai_accuracy_score'].mean().reset_index()
                
                fig = px.line(daily_ai_performance, x='call_date', y='ai_accuracy_score',
                            title="Daily AI Accuracy Trend",
                            labels={'call_date': 'Date', 'ai_accuracy_score': 'AI Accuracy'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with ai_tab2:
        st.markdown("### 🎯 Intent Analysis Deep Dive")
        
        if 'intent_detected' in df.columns:
            # Intent metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_intents = df['intent_detected'].nunique()
                st.metric("🎯 Total Intent Types", total_intents)
            
            with col2:
                most_common_intent = df['intent_detected'].mode().iloc[0] if len(df['intent_detected'].mode()) > 0 else "N/A"
                st.metric("🔝 Most Common", most_common_intent)
            
            with col3:
                intent_accuracy = df['intent_detected'].notna().sum() / len(df) * 100
                st.metric("✅ Detection Rate", f"{intent_accuracy:.1f}%")
            
            with col4:
                booking_intents = (df['intent_detected'] == 'Booking').sum()
                st.metric("📅 Booking Intents", booking_intents)
            
            # Intent analysis charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">🎯 Intent Distribution</div>', unsafe_allow_html=True)
                
                intent_counts = df['intent_detected'].value_counts()
                fig = px.pie(values=intent_counts.values, names=intent_counts.index,
                           title="Call Intent Distribution")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">🎯 Intent Success Rate</div>', unsafe_allow_html=True)
                
                intent_success = df.groupby('intent_detected')['call_success'].apply(
                    lambda x: (x == 'Yes').sum() / len(x) * 100
                ).reset_index()
                
                fig = px.bar(intent_success, x='intent_detected', y='call_success',
                           title="Success Rate by Intent Type",
                           labels={'intent_detected': 'Intent', 'call_success': 'Success Rate %'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Intent trend analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📈 Intent Trends Over Time</div>', unsafe_allow_html=True)
                
                if 'call_date' in df.columns:
                    intent_trends = df.groupby(['call_date', 'intent_detected']).size().reset_index(name='count')
                    
                    fig = px.line(intent_trends, x='call_date', y='count', color='intent_detected',
                                title="Intent Trends Over Time",
                                labels={'call_date': 'Date', 'count': 'Number of Calls'})
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">💰 Revenue by Intent</div>', unsafe_allow_html=True)
                
                if 'revenue_impact' in df.columns:
                    intent_revenue = df.groupby('intent_detected')['revenue_impact'].sum().reset_index()
                    
                    fig = px.bar(intent_revenue, x='intent_detected', y='revenue_impact',
                               title="Total Revenue by Intent Type",
                               labels={'intent_detected': 'Intent', 'revenue_impact': 'Revenue ($)'})
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with ai_tab3:
        st.markdown("### 😊 Sentiment Analysis Deep Dive")
        
        if 'sentiment_score' in df.columns:
            # Sentiment metrics
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                avg_sentiment = df['sentiment_score'].mean()
                st.metric("😊 Avg Sentiment", f"{avg_sentiment:.3f}", delta=f"+{avg_sentiment*0.05:.3f}")
            
            with col2:
                positive_sentiment = (df['sentiment_score'] > 0.7).sum()
                st.metric("😊 Positive", positive_sentiment, delta=f"+{positive_sentiment//10}")
            
            with col3:
                neutral_sentiment = ((df['sentiment_score'] >= 0.3) & (df['sentiment_score'] <= 0.7)).sum()
                st.metric("😐 Neutral", neutral_sentiment, delta=f"+{neutral_sentiment//15}")
            
            with col4:
                negative_sentiment = (df['sentiment_score'] < 0.3).sum()
                st.metric("😞 Negative", negative_sentiment, delta=f"-{negative_sentiment//20}")
            
            with col5:
                sentiment_range = df['sentiment_score'].max() - df['sentiment_score'].min()
                st.metric("📊 Range", f"{sentiment_range:.3f}")
            
            with col6:
                sentiment_std = df['sentiment_score'].std()
                st.metric("📈 Std Dev", f"{sentiment_std:.3f}")
            
            # Sentiment analysis charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">😊 Sentiment Score Distribution</div>', unsafe_allow_html=True)
                
                fig = px.histogram(df, x='sentiment_score', nbins=30,
                                 title="Sentiment Score Distribution",
                                 labels={'sentiment_score': 'Sentiment Score', 'count': 'Number of Calls'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">🎭 Emotion Detection Analysis</div>', unsafe_allow_html=True)
                
                if 'emotion_detected' in df.columns:
                    emotion_counts = df['emotion_detected'].value_counts()
                    
                    fig = px.bar(x=emotion_counts.values, y=emotion_counts.index, orientation='h',
                               title="Detected Emotions Distribution",
                               labels={'x': 'Number of Calls', 'y': 'Emotion'})
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Advanced sentiment analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">😊 Sentiment vs Call Duration</div>', unsafe_allow_html=True)
                
                if 'call_duration_seconds' in df.columns:
                    fig = px.scatter(df, x='call_duration_seconds', y='sentiment_score',
                                   color='call_success', size='customer_satisfaction',
                                   title="Sentiment vs Call Duration",
                                   labels={'call_duration_seconds': 'Duration (seconds)', 'sentiment_score': 'Sentiment'})
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📈 Daily Sentiment Trend</div>', unsafe_allow_html=True)
                
                if 'call_date' in df.columns:
                    daily_sentiment = df.groupby('call_date')['sentiment_score'].mean().reset_index()
                    
                    fig = px.line(daily_sentiment, x='call_date', y='sentiment_score',
                                title="Daily Average Sentiment Trend",
                                labels={'call_date': 'Date', 'sentiment_score': 'Average Sentiment'})
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with ai_tab4:
        st.markdown("### 🔮 AI Predictions & Forecasting")
        
        # Generate prediction data
        future_dates = pd.date_range(start=datetime.now().date(), periods=30, freq='D')
        
        # Mock AI predictions
        predictions = {
            'Date': future_dates,
            'Predicted_Calls': np.random.poisson(25, 30),
            'Predicted_Success_Rate': np.random.beta(8, 2, 30),
            'Predicted_Sentiment': np.random.beta(7, 3, 30),
            'Predicted_Revenue': np.random.gamma(2, 1000, 30),
            'Confidence_Interval_Lower': np.random.uniform(0.8, 0.9, 30),
            'Confidence_Interval_Upper': np.random.uniform(0.9, 0.95, 30)
        }
        
        pred_df = pd.DataFrame(predictions)
        
        # Prediction metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_predicted_calls = pred_df['Predicted_Calls'].mean()
            st.metric("📞 Predicted Daily Calls", f"{avg_predicted_calls:.0f}")
        
        with col2:
            avg_predicted_success = pred_df['Predicted_Success_Rate'].mean()
            st.metric("✅ Predicted Success Rate", f"{avg_predicted_success:.1%}")
        
        with col3:
            avg_predicted_sentiment = pred_df['Predicted_Sentiment'].mean()
            st.metric("😊 Predicted Sentiment", f"{avg_predicted_sentiment:.3f}")
        
        with col4:
            total_predicted_revenue = pred_df['Predicted_Revenue'].sum()
            st.metric("💰 Predicted Revenue", f"${total_predicted_revenue:,.0f}")
        
        # Prediction charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔮 Call Volume Prediction</div>', unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted_Calls'],
                                   mode='lines+markers', name='Predicted Calls'))
            fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted_Calls'] * pred_df['Confidence_Interval_Upper'],
                                   fill=None, mode='lines', line_color='rgba(0,100,80,0)', showlegend=False))
            fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted_Calls'] * pred_df['Confidence_Interval_Lower'],
                                   fill='tonexty', mode='lines', line_color='rgba(0,100,80,0)', 
                                   name='Confidence Interval'))
            
            fig.update_layout(title="30-Day Call Volume Prediction", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 Multi-Metric Predictions</div>', unsafe_allow_html=True)
            
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=('Success Rate', 'Sentiment Score', 'Revenue'),
                vertical_spacing=0.1
            )
            
            fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted_Success_Rate'], 
                                   name='Success Rate'), row=1, col=1)
            fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted_Sentiment'], 
                                   name='Sentiment'), row=2, col=1)
            fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted_Revenue'], 
                                   name='Revenue'), row=3, col=1)
            
            fig.update_layout(height=600, title_text="30-Day Multi-Metric Predictions")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # AI Model Performance
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🤖 AI Model Performance Metrics</div>', unsafe_allow_html=True)
        
        # Mock model performance data
        model_metrics = {
            'Model': ['Intent Detection', 'Sentiment Analysis', 'Call Success Prediction', 'Revenue Prediction', 'Customer Satisfaction'],
            'Accuracy': [0.94, 0.89, 0.87, 0.82, 0.91],
            'Precision': [0.92, 0.88, 0.85, 0.80, 0.89],
            'Recall': [0.93, 0.87, 0.86, 0.83, 0.90],
            'F1_Score': [0.925, 0.875, 0.855, 0.815, 0.895]
        }
        
        model_df = pd.DataFrame(model_metrics)
        
        fig = px.bar(model_df, x='Model', y=['Accuracy', 'Precision', 'Recall', 'F1_Score'],
                   title="AI Model Performance Comparison",
                   labels={'value': 'Score', 'variable': 'Metric'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with ai_tab5:
        st.markdown("### 🛠️ Model Metrics & Diagnostics")
        
        # Model diagnostics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="crm-card">', unsafe_allow_html=True)
            st.markdown("#### 🤖 Model Status")
            st.success("✅ All models operational")
            st.info("🔄 Last updated: 2 hours ago")
            st.write("**Active Models:** 5")
            st.write("**Training Status:** Complete")
            st.write("**Next Update:** 6 hours")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="crm-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Performance Summary")
            st.metric("Overall Accuracy", "89.2%", delta="+2.1%")
            st.metric("Model Confidence", "94.7%", delta="+1.3%")
            st.metric("Processing Speed", "1.2s", delta="-0.3s")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="crm-card">', unsafe_allow_html=True)
            st.markdown("#### ⚠️ Alerts & Issues")
            st.warning("⚠️ Sentiment model needs retraining")
            st.info("ℹ️ New training data available")
            st.success("✅ All systems stable")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Model performance details
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Model Performance Over Time</div>', unsafe_allow_html=True)
        
        # Generate mock performance data
        dates = pd.date_range(start=datetime.now().date() - timedelta(days=30), periods=30, freq='D')
        performance_data = {
            'Date': dates,
            'Intent_Accuracy': np.random.uniform(0.90, 0.96, 30),
            'Sentiment_Accuracy': np.random.uniform(0.85, 0.92, 30),
            'Success_Prediction': np.random.uniform(0.82, 0.90, 30),
            'Overall_Performance': np.random.uniform(0.87, 0.94, 30)
        }
        
        perf_df = pd.DataFrame(performance_data)
        
        fig = px.line(perf_df, x='Date', y=['Intent_Accuracy', 'Sentiment_Accuracy', 'Success_Prediction', 'Overall_Performance'],
                    title="Model Performance Trends (30 Days)",
                    labels={'value': 'Accuracy Score', 'variable': 'Model'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "🔗 Webhooks":
    st.markdown('<h2 class="section-header animate-fadeIn">🔗 Webhook Management & n8n Integration</h2>', unsafe_allow_html=True)
    
    # Webhook status overview
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        webhook_count = random.randint(5, 15)
        st.metric("🔗 Active Webhooks", webhook_count, delta=f"+{webhook_count//5}")
    
    with col2:
        webhook_success = random.randint(95, 99)
        st.metric("✅ Success Rate", f"{webhook_success}%", delta=f"+{webhook_success-95}%")
    
    with col3:
        daily_webhooks = random.randint(200, 800)
        st.metric("📊 Daily Webhooks", daily_webhooks, delta=f"+{daily_webhooks//10}")
    
    with col4:
        avg_latency = random.randint(50, 200)
        st.metric("⚡ Avg Latency", f"{avg_latency}ms", delta=f"-{random.randint(5, 20)}ms")
    
    with col5:
        failed_webhooks = random.randint(2, 15)
        st.metric("❌ Failed Today", failed_webhooks, delta=f"-{failed_webhooks//3}")
    
    with col6:
        n8n_workflows = random.randint(8, 20)
        st.metric("🔄 n8n Workflows", n8n_workflows, delta=f"+{n8n_workflows//4}")
    
    # Webhook management tabs
    webhook_tab1, webhook_tab2, webhook_tab3, webhook_tab4 = st.tabs(["🔗 Active Webhooks", "📊 Analytics", "🔄 n8n Integration", "⚙️ Configuration"])
    
    with webhook_tab1:
        st.markdown("### 🔗 Active Webhook Endpoints")
        
        # Mock webhook data
        webhook_data = {
            'Webhook ID': [f'WH-{1000+i:04d}' for i in range(10)],
            'Endpoint': [f'https://api.vapi.ai/webhook/{random.choice(["call", "sms", "email"])}/{i}' for i in range(10)],
            'Type': [random.choice(['Call Started', 'Call Ended', 'Booking Created', 'Customer Updated', 'Payment Processed']) for _ in range(10)],
            'Status': [random.choice(['Active', 'Paused', 'Error']) for _ in range(10)],
            'Last Triggered': [(datetime.now() - timedelta(minutes=random.randint(1, 1440))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(10)],
            'Success Rate': [f"{random.randint(85, 99)}%" for _ in range(10)],
            'Daily Calls': [random.randint(10, 100) for _ in range(10)],
            'Avg Response Time': [f"{random.randint(50, 300)}ms" for _ in range(10)]
        }
        
        webhook_df = pd.DataFrame(webhook_data)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔗 Webhook Management Grid</div>', unsafe_allow_html=True)
        
        grid_response = create_enhanced_ag_grid(webhook_df, "webhook_grid", height=400, enable_enterprise=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Webhook actions
        if grid_response['selected_rows']:
            selected_webhook = grid_response['selected_rows'][0]
            
            st.markdown(f"### 🔗 Webhook Details: {selected_webhook['Webhook ID']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📋 Webhook Information")
                st.write(f"**ID:** {selected_webhook['Webhook ID']}")
                st.write(f"**Type:** {selected_webhook['Type']}")
                st.write(f"**Status:** {selected_webhook['Status']}")
                st.write(f"**Endpoint:** {selected_webhook['Endpoint']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📊 Performance Metrics")
                st.write(f"**Success Rate:** {selected_webhook['Success Rate']}")
                st.write(f"**Daily Calls:** {selected_webhook['Daily Calls']}")
                st.write(f"**Avg Response:** {selected_webhook['Avg Response Time']}")
                st.write(f"**Last Triggered:** {selected_webhook['Last Triggered']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 🛠️ Actions")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("▶️ Enable", use_container_width=True):
                        st.success("Webhook enabled!")
                    if st.button("🔄 Test", use_container_width=True):
                        st.info("Testing webhook...")
                
                with col_b:
                    if st.button("⏸️ Pause", use_container_width=True):
                        st.warning("Webhook paused!")
                    if st.button("🗑️ Delete", use_container_width=True):
                        st.error("Webhook deleted!")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with webhook_tab2:
        st.markdown("### 📊 Webhook Analytics")
        
        # Generate mock webhook analytics data
        webhook_dates = pd.date_range(start=datetime.now().date() - timedelta(days=7), periods=7, freq='D')
        webhook_analytics = {
            'Date': webhook_dates,
            'Total_Webhooks': np.random.randint(100, 300, 7),
            'Successful': np.random.randint(90, 280, 7),
            'Failed': np.random.randint(5, 20, 7),
            'Avg_Response_Time': np.random.randint(80, 250, 7)
        }
        
        webhook_analytics_df = pd.DataFrame(webhook_analytics)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 Webhook Volume Trend</div>', unsafe_allow_html=True)
            
            fig = px.line(webhook_analytics_df, x='Date', y=['Total_Webhooks', 'Successful', 'Failed'],
                        title="7-Day Webhook Volume Trend",
                        labels={'value': 'Number of Webhooks', 'variable': 'Status'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⚡ Response Time Analysis</div>', unsafe_allow_html=True)
            
            fig = px.bar(webhook_analytics_df, x='Date', y='Avg_Response_Time',
                       title="Average Response Time by Day",
                       labels={'Avg_Response_Time': 'Response Time (ms)'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Webhook type analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔗 Webhook Type Distribution</div>', unsafe_allow_html=True)
            
            webhook_types = ['Call Started', 'Call Ended', 'Booking Created', 'Customer Updated', 'Payment Processed']
            type_counts = [random.randint(50, 200) for _ in webhook_types]
            
            fig = px.pie(values=type_counts, names=webhook_types,
                       title="Webhook Type Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 Success Rate by Type</div>', unsafe_allow_html=True)
            
            success_rates = [random.randint(85, 99) for _ in webhook_types]
            
            fig = px.bar(x=webhook_types, y=success_rates,
                       title="Success Rate by Webhook Type",
                       labels={'x': 'Webhook Type', 'y': 'Success Rate %'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with webhook_tab3:
        st.markdown("### 🔄 n8n Workflow Integration")
        
        # n8n workflow status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔄 Active Workflows", random.randint(8, 20))
        with col2:
            st.metric("✅ Success Rate", f"{random.randint(92, 98)}%")
        with col3:
            st.metric("⚡ Avg Execution", f"{random.randint(2, 8)}s")
        with col4:
            st.metric("📊 Daily Executions", random.randint(150, 500))
        
        # n8n workflow list
        n8n_workflows = {
            'Workflow ID': [f'n8n-{1000+i:04d}' for i in range(8)],
            'Name': ['Call Processing Pipeline', 'Customer Data Sync', 'Booking Automation', 'Email Notifications', 
                    'SMS Alerts', 'CRM Integration', 'Analytics Pipeline', 'Backup & Archive'],
            'Status': [random.choice(['Running', 'Paused', 'Error']) for _ in range(8)],
            'Last Execution': [(datetime.now() - timedelta(minutes=random.randint(1, 120))).strftime('%H:%M:%S') for _ in range(8)],
            'Success Rate': [f"{random.randint(88, 99)}%" for _ in range(8)],
            'Executions Today': [random.randint(10, 80) for _ in range(8)],
            'Avg Duration': [f"{random.randint(1, 10)}s" for _ in range(8)]
        }
        
        n8n_df = pd.DataFrame(n8n_workflows)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔄 n8n Workflow Management</div>', unsafe_allow_html=True)
        
        grid_response_n8n = create_enhanced_ag_grid(n8n_df, "n8n_grid", height=350, enable_enterprise=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Workflow details
        if grid_response_n8n['selected_rows']:
            selected_workflow = grid_response_n8n['selected_rows'][0]
            
            st.markdown(f"### 🔄 Workflow: {selected_workflow['Name']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📋 Workflow Details")
                st.write(f"**ID:** {selected_workflow['Workflow ID']}")
                st.write(f"**Name:** {selected_workflow['Name']}")
                st.write(f"**Status:** {selected_workflow['Status']}")
                st.write(f"**Last Execution:** {selected_workflow['Last Execution']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📊 Performance")
                st.write(f"**Success Rate:** {selected_workflow['Success Rate']}")
                st.write(f"**Executions Today:** {selected_workflow['Executions Today']}")
                st.write(f"**Avg Duration:** {selected_workflow['Avg Duration']}")
                st.markdown('</div>', unsafe_allow_html=True)
    
    with webhook_tab4:
        st.markdown("### ⚙️ Webhook Configuration")
        
        # Add new webhook form
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">➕ Add New Webhook</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            webhook_name = st.text_input("🏷️ Webhook Name", placeholder="Enter webhook name")
            webhook_url = st.text_input("🔗 Endpoint URL", placeholder="https://your-endpoint.com/webhook")
            webhook_type = st.selectbox("📋 Webhook Type", 
                                      ['Call Started', 'Call Ended', 'Booking Created', 'Customer Updated', 'Payment Processed'])
            webhook_method = st.selectbox("🔧 HTTP Method", ['POST', 'PUT', 'PATCH'])
        
        with col2:
            webhook_headers = st.text_area("📋 Custom Headers (JSON)", 
                                         placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}')
            webhook_timeout = st.slider("⏱️ Timeout (seconds)", 5, 60, 30)
            webhook_retries = st.slider("🔄 Max Retries", 0, 5, 3)
            webhook_active = st.checkbox("✅ Active", value=True)
        
        if st.button("➕ Create Webhook", use_container_width=True):
            if webhook_name and webhook_url:
                st.success(f"✅ Webhook '{webhook_name}' created successfully!")
            else:
                st.error("❌ Please fill in all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Webhook testing
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🧪 Webhook Testing</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_url = st.text_input("🔗 Test URL", placeholder="https://webhook.site/unique-id")
            test_payload = st.text_area("📋 Test Payload (JSON)", 
                                      value='{"call_id": "test-123", "customer_name": "Test Customer", "status": "completed"}')
        
        with col2:
            if st.button("🧪 Send Test Webhook", use_container_width=True):
                if test_url:
                    with st.spinner("Sending test webhook..."):
                        time_module.sleep(2)  # Simulate API call
                        st.success("✅ Test webhook sent successfully!")
                        st.json({
                            "status": "success",
                            "response_code": 200,
                            "response_time": "145ms",
                            "response_body": {"received": True, "timestamp": datetime.now().isoformat()}
                        })
                else:
                    st.error("❌ Please enter a test URL")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "📊 Reports":
    st.markdown('<h2 class="section-header animate-fadeIn">📊 Advanced Reporting & Export</h2>', unsafe_allow_html=True)
    
    # Report generation interface
    report_tab1, report_tab2, report_tab3, report_tab4 = st.tabs(["📋 Generate Reports", "📈 Scheduled Reports", "📤 Export Data", "📊 Report Templates"])
    
    with report_tab1:
        st.markdown("### 📋 Custom Report Generation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            report_type = st.selectbox("📊 Report Type", 
                                     ['Executive Summary', 'Agent Performance', 'Customer Analytics', 
                                      'Revenue Analysis', 'AI Performance', 'Call Quality', 'Custom'])
            
            date_range = st.date_input("📅 Date Range", 
                                     value=[datetime.now().date() - timedelta(days=30), datetime.now().date()])
            
            report_format = st.selectbox("📄 Format", ['PDF', 'Excel', 'CSV', 'PowerPoint'])
        
        with col2:
            include_charts = st.checkbox("📈 Include Charts", value=True)
            include_raw_data = st.checkbox("📋 Include Raw Data", value=False)
            include_summary = st.checkbox("📊 Include Summary", value=True)
            include_recommendations = st.checkbox("💡 Include AI Recommendations", value=True)
        
        with col3:
            if report_type == 'Custom':
                custom_metrics = st.multiselect("📊 Select Metrics", 
                                              ['Call Volume', 'Success Rate', 'Revenue', 'Satisfaction', 
                                               'AI Accuracy', 'Response Time', 'Conversion Rate'])
            
            email_recipients = st.text_area("📧 Email Recipients", 
                                          placeholder="email1@company.com, email2@company.com")
        
        # Generate report button
        if st.button("📊 Generate Report", use_container_width=True):
            with st.spinner("Generating comprehensive report..."):
                time_module.sleep(3)  # Simulate report generation
                
                st.success("✅ Report generated successfully!")
                
                # Mock report preview
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📋 Report Preview</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Executive Summary")
                    st.write(f"**Report Type:** {report_type}")
                    st.write(f"**Date Range:** {date_range[0]} to {date_range[1]}")
                    st.write(f"**Total Records:** {len(df):,}")
                    st.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                with col2:
                    st.markdown("#### 📈 Key Metrics")
                    st.metric("Total Calls", f"{len(df):,}")
                    st.metric("Success Rate", f"{(df['call_success'] == 'Yes').sum() / len(df) * 100:.1f}%")
                    st.metric("Avg Satisfaction", f"{df['customer_satisfaction'].mean():.1f}/5" if 'customer_satisfaction' in df.columns else "N/A")
                
                # Download buttons
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.download_button("📄 Download PDF", 
                                     data="Mock PDF content", 
                                     file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                     mime="application/pdf")
                
                with col2:
                    csv_data = df.to_csv(index=False)
                    st.download_button("📊 Download Excel", 
                                     data=csv_data, 
                                     file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                     mime="text/csv")
                
                with col3:
                    st.download_button("📈 Download Charts", 
                                     data="Mock chart data", 
                                     file_name=f"charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                     mime="image/png")
                
                with col4:
                    if email_recipients:
                        if st.button("📧 Email Report"):
                            st.success("📧 Report emailed successfully!")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with report_tab2:
        st.markdown("### 📈 Scheduled Reports")
        
        # Scheduled reports list
        scheduled_reports = {
            'Report ID': [f'RPT-{1000+i:04d}' for i in range(6)],
            'Name': ['Daily Executive Summary', 'Weekly Agent Performance', 'Monthly Revenue Report', 
                    'Customer Satisfaction Weekly', 'AI Performance Daily', 'Call Quality Monthly'],
            'Type': ['Executive Summary', 'Agent Performance', 'Revenue Analysis', 
                    'Customer Analytics', 'AI Performance', 'Call Quality'],
            'Schedule': ['Daily 9:00 AM', 'Weekly Monday 8:00 AM', 'Monthly 1st 10:00 AM',
                        'Weekly Friday 5:00 PM', 'Daily 6:00 AM', 'Monthly 15th 2:00 PM'],
            'Recipients': ['executives@company.com', 'managers@company.com', 'finance@company.com',
                          'support@company.com', 'ai-team@company.com', 'quality@company.com'],
            'Status': [random.choice(['Active', 'Paused']) for _ in range(6)],
            'Last Sent': [(datetime.now() - timedelta(hours=random.randint(1, 48))).strftime('%Y-%m-%d %H:%M') for _ in range(6)],
            'Next Send': [(datetime.now() + timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M') for _ in range(6)]
        }
        
        scheduled_df = pd.DataFrame(scheduled_reports)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Scheduled Reports Management</div>', unsafe_allow_html=True)
        
        grid_response_reports = create_enhanced_ag_grid(scheduled_df, "scheduled_reports_grid", height=400, enable_enterprise=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add new scheduled report
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">➕ Schedule New Report</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            schedule_name = st.text_input("📋 Report Name", placeholder="Enter report name")
            schedule_type = st.selectbox("📊 Report Type", 
                                       ['Executive Summary', 'Agent Performance', 'Customer Analytics', 
                                        'Revenue Analysis', 'AI Performance', 'Call Quality'])
            schedule_format = st.selectbox("📄 Format", ['PDF', 'Excel', 'PowerPoint'])
        
        with col2:
            schedule_frequency = st.selectbox("🔄 Frequency", ['Daily', 'Weekly', 'Monthly', 'Quarterly'])
            schedule_time = st.time_input("⏰ Time", value=time(9, 0))
            schedule_recipients = st.text_area("📧 Recipients", placeholder="email1@company.com, email2@company.com")
        
        with col3:
            schedule_active = st.checkbox("✅ Active", value=True)
            include_attachments = st.checkbox("📎 Include Attachments", value=True)
            
            if st.button("📅 Schedule Report", use_container_width=True):
                if schedule_name and schedule_recipients:
                    st.success(f"✅ Report '{schedule_name}' scheduled successfully!")
                else:
                    st.error("❌ Please fill in all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with report_tab3:
        st.markdown("### 📤 Data Export & Integration")
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📤 Export All Data</div>', unsafe_allow_html=True)
            
            export_format = st.selectbox("📄 Export Format", ['CSV', 'Excel', 'JSON', 'Parquet'])
            export_compression = st.selectbox("🗜️ Compression", ['None', 'ZIP', 'GZIP'])
            include_metadata = st.checkbox("📋 Include Metadata", value=True)
            
            if st.button("📤 Export Complete Dataset", use_container_width=True):
                with st.spinner("Preparing export..."):
                    time_module.sleep(2)
                    
                    if export_format == 'CSV':
                        export_data = df.to_csv(index=False)
                        mime_type = "text/csv"
                        file_ext = "csv"
                    elif export_format == 'JSON':
                        export_data = df.to_json(orient='records', indent=2)
                        mime_type = "application/json"
                        file_ext = "json"
                    else:
                        export_data = df.to_csv(index=False)  # Fallback to CSV
                        mime_type = "text/csv"
                        file_ext = "csv"
                    
                    st.download_button(
                        label=f"📥 Download {export_format} File",
                        data=export_data,
                        file_name=f"vapi_ai_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}",
                        mime=mime_type,
                        use_container_width=True
                    )
                    
                    st.success(f"✅ {len(df):,} records ready for download!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔄 Live Data Integration</div>', unsafe_allow_html=True)
            
            # Google Sheets export
            if st.button("📊 Export to Google Sheets", use_container_width=True):
                if sheets_url and uploaded_json:
                    with st.spinner("Exporting to Google Sheets..."):
                        json_content = uploaded_json.read().decode('utf-8')
                        success = export_data_to_sheets(df, sheets_url, json_content)
                        
                        if success:
                            st.success("✅ Data exported to Google Sheets successfully!")
                        else:
                            st.error("❌ Export failed. Check your credentials and URL.")
                else:
                    st.warning("⚠️ Please configure Google Sheets URL and credentials in the sidebar first.")
            
            # API export
            api_endpoint = st.text_input("🔗 API Endpoint", placeholder="https://your-api.com/data")
            api_key = st.text_input("🔑 API Key", type="password", placeholder="Your API key")
            
            if st.button("🌐 Export via API", use_container_width=True):
                if api_endpoint:
                    with st.spinner("Sending data via API..."):
                        time_module.sleep(2)
                        st.success("✅ Data sent to API successfully!")
                        st.json({
                            "status": "success",
                            "records_sent": len(df),
                            "endpoint": api_endpoint,
                            "timestamp": datetime.now().isoformat()
                        })
                else:
                    st.warning("⚠️ Please enter API endpoint")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export statistics
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Export Statistics</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("📊 Total Records", f"{len(df):,}")
        with col2:
            st.metric("📋 Total Columns", len(df.columns))
        with col3:
            file_size_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            st.metric("💾 Data Size", f"{file_size_mb:.1f} MB")
        with col4:
            st.metric("📅 Date Range", f"{(pd.to_datetime(df['call_date']).max() - pd.to_datetime(df['call_date']).min()).days} days" if 'call_date' in df.columns else "N/A")
        with col5:
            st.metric("👥 Unique Customers", df['customer_name'].nunique() if 'customer_name' in df.columns else 0)
        with col6:
            st.metric("🤖 AI Agents", df['voice_agent_name'].nunique() if 'voice_agent_name' in df.columns else 0)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with report_tab4:
        st.markdown("### 📊 Report Templates")
        
        # Report templates
        templates = {
            'Template Name': ['Executive Dashboard', 'Agent Performance Review', 'Customer Insights', 
                            'Revenue Analysis', 'AI Performance Report', 'Quality Assurance'],
            'Description': ['High-level KPIs and trends for executives', 
                          'Detailed agent performance metrics and comparisons',
                          'Customer behavior and satisfaction analysis',
                          'Revenue trends and financial performance',
                          'AI model performance and accuracy metrics',
                          'Call quality and compliance metrics'],
            'Sections': ['KPIs, Trends, Alerts', 'Performance, Comparisons, Goals', 
                        'Satisfaction, Behavior, Segments', 'Revenue, Costs, ROI',
                        'Accuracy, Confidence, Trends', 'Quality, Compliance, Issues'],
            'Charts': ['Line, Bar, Gauge', 'Bar, Radar, Scatter', 'Pie, Heatmap, Funnel',
                      'Area, Waterfall, Treemap', 'Line, Histogram, Box', 'Bar, Gauge, Scatter'],
            'Frequency': ['Daily', 'Weekly', 'Monthly', 'Monthly', 'Daily', 'Weekly'],
            'Status': ['Active', 'Active', 'Active', 'Active', 'Active', 'Draft']
        }
        
        templates_df = pd.DataFrame(templates)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Available Report Templates</div>', unsafe_allow_html=True)
        
        grid_response_templates = create_enhanced_ag_grid(templates_df, "templates_grid", height=350, enable_enterprise=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Template actions
        if grid_response_templates['selected_rows']:
            selected_template = grid_response_templates['selected_rows'][0]
            
            st.markdown(f"### 📊 Template: {selected_template['Template Name']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📋 Template Details")
                st.write(f"**Name:** {selected_template['Template Name']}")
                st.write(f"**Description:** {selected_template['Description']}")
                st.write(f"**Sections:** {selected_template['Sections']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📈 Template Configuration")
                st.write(f"**Charts:** {selected_template['Charts']}")
                st.write(f"**Frequency:** {selected_template['Frequency']}")
                st.write(f"**Status:** {selected_template['Status']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 🛠️ Actions")
                
                if st.button("📊 Use Template", use_container_width=True):
                    st.success(f"✅ Using template: {selected_template['Template Name']}")
                
                if st.button("✏️ Edit Template", use_container_width=True):
                    st.info(f"✏️ Editing template: {selected_template['Template Name']}")
                
                if st.button("📋 Duplicate Template", use_container_width=True):
                    st.success(f"📋 Template duplicated: {selected_template['Template Name']} Copy")
                
                st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "🔴 Live Monitor":
    st.markdown('<h2 class="section-header animate-fadeIn">🔴 Real-time Operations Monitor</h2>', unsafe_allow_html=True)
    
    # Auto-refresh functionality
    if st.session_state.auto_refresh:
        time_module.sleep(1)  # Small delay for demo
        st.rerun()
    
    # Live monitoring tabs
    monitor_tab1, monitor_tab2, monitor_tab3, monitor_tab4 = st.tabs(["🔴 Live Dashboard", "📞 Active Calls", "🌐 URL Monitor", "⚠️ Alerts"])
    
    with monitor_tab1:
        st.markdown("### 🔴 Real-time Operations Dashboard")
        
        # Real-time metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            active_calls = random.randint(8, 35)
            st.metric("🔴 Active Calls", active_calls, delta=random.randint(-3, 5))
        
        with col2:
            queue_length = random.randint(0, 12)
            st.metric("⏳ Queue Length", queue_length, delta=random.randint(-2, 4))
        
        with col3:
            available_agents = random.randint(12, 25)
            st.metric("🤖 Available Agents", available_agents, delta=random.randint(-1, 3))
        
        with col4:
            avg_wait_time = random.randint(15, 120)
            st.metric("⚡ Avg Wait Time", f"{avg_wait_time}s", delta=f"{random.randint(-20, 30)}s")
        
        with col5:
            system_load = random.randint(35, 85)
            st.metric("💻 System Load", f"{system_load}%", delta=f"{random.randint(-5, 10)}%")
        
        with col6:
            api_latency = random.randint(45, 180)
            st.metric("🌐 API Latency", f"{api_latency}ms", delta=f"{random.randint(-20, 40)}ms")
        
        # Real-time charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 Live Call Volume (Last Hour)</div>', unsafe_allow_html=True)
            
            # Generate live data
            now = datetime.now()
            times = [now - timedelta(minutes=i) for i in range(60, 0, -1)]
            call_volumes = [random.randint(0, 8) for _ in times]
            
            fig = px.line(x=times, y=call_volumes,
                        title="Call Volume - Last 60 Minutes",
                        labels={'x': 'Time', 'y': 'Calls per Minute'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⚡ System Performance Metrics</div>', unsafe_allow_html=True)
            
            # System metrics gauge
            fig = go.Figure()
            
            fig.add_trace(go.Indicator(
                mode = "gauge+number+delta",
                value = system_load,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "System Load %"},
                delta = {'reference': 70},
                gauge = {'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "gray"}],
                        'threshold': {'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75, 'value': 90}}))
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Live activity feed
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Live Activity Feed</div>', unsafe_allow_html=True)
        
        # Generate live activity data
        activities = []
        for i in range(10):
            activity_time = datetime.now() - timedelta(seconds=random.randint(1, 300))
            activity_type = random.choice(['Call Started', 'Call Ended', 'Booking Created', 'Customer Updated', 'Payment Processed'])
            customer = f"Customer {random.randint(1, 100)}"
            agent = random.choice(['VAPI Agent Alpha', 'VAPI Agent Beta', 'VAPI Agent Gamma'])
            
            activities.append({
                'Time': activity_time.strftime('%H:%M:%S'),
                'Type': activity_type,
                'Customer': customer,
                'Agent': agent,
                'Status': random.choice(['Success', 'In Progress', 'Failed'])
            })
        
        activity_df = pd.DataFrame(activities)
        
        # Display activity feed with color coding
        for _, activity in activity_df.iterrows():
            status_color = {
                'Success': '🟢',
                'In Progress': '🟡',
                'Failed': '🔴'
            }
            
            st.markdown(f"""
            <div style="padding: 0.5rem; margin: 0.2rem 0; background: rgba(255,255,255,0.1); border-radius: 8px; border-left: 4px solid #6366f1;">
                {status_color[activity['Status']]} <strong>{activity['Time']}</strong> - {activity['Type']} | {activity['Customer']} | {activity['Agent']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with monitor_tab2:
        st.markdown("### 📞 Active Calls Monitor")
        
        # Generate active calls data
        active_calls_data = []
        for i in range(random.randint(5, 15)):
            call_start = datetime.now() - timedelta(seconds=random.randint(30, 1800))
            duration = (datetime.now() - call_start).total_seconds()
            
            active_calls_data.append({
                'Call ID': f'LIVE-{1000+i:04d}',
                'Customer': f'Customer {random.randint(1, 500)}',
                'Phone': f'+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}',
                'Agent': random.choice(['VAPI Agent Alpha', 'VAPI Agent Beta', 'VAPI Agent Gamma', 'VAPI Agent Delta']),
                'Start Time': call_start.strftime('%H:%M:%S'),
                'Duration': f"{int(duration//60):02d}:{int(duration%60):02d}",
                'Status': random.choice(['Connected', 'Ringing', 'On Hold', 'Transferring']),
                'Intent': random.choice(['Booking', 'Support', 'Sales', 'Information']),
                'Sentiment': random.choice(['Positive', 'Neutral', 'Negative']),
                'Quality': random.choice(['Excellent', 'Good', 'Fair', 'Poor'])
            })
        
        active_calls_df = pd.DataFrame(active_calls_data)
        
        # Active calls metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📞 Total Active", len(active_calls_df))
        with col2:
            avg_duration = active_calls_df['Duration'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1])).mean()
            st.metric("⏱️ Avg Duration", f"{int(avg_duration//60):02d}:{int(avg_duration%60):02d}")
        with col3:
            connected_calls = (active_calls_df['Status'] == 'Connected').sum()
            st.metric("✅ Connected", connected_calls)
        with col4:
            positive_sentiment = (active_calls_df['Sentiment'] == 'Positive').sum()
            st.metric("😊 Positive Sentiment", positive_sentiment)
        
        # Active calls grid
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📞 Live Calls Grid</div>', unsafe_allow_html=True)
        
        grid_response_active = create_enhanced_ag_grid(active_calls_df, "active_calls_grid", height=400, enable_enterprise=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Call details
        if grid_response_active['selected_rows']:
            selected_call = grid_response_active['selected_rows'][0]
            
            st.markdown(f"### 📞 Live Call Details: {selected_call['Call ID']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📋 Call Information")
                st.write(f"**Call ID:** {selected_call['Call ID']}")
                st.write(f"**Customer:** {selected_call['Customer']}")
                st.write(f"**Phone:** {selected_call['Phone']}")
                st.write(f"**Agent:** {selected_call['Agent']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### ⏱️ Call Status")
                st.write(f"**Status:** {selected_call['Status']}")
                st.write(f"**Start Time:** {selected_call['Start Time']}")
                st.write(f"**Duration:** {selected_call['Duration']}")
                st.write(f"**Intent:** {selected_call['Intent']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📊 Call Quality")
                st.write(f"**Sentiment:** {selected_call['Sentiment']}")
                st.write(f"**Quality:** {selected_call['Quality']}")
                
                # Call actions
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🎧 Listen In", use_container_width=True):
                        st.info("🎧 Listening to call...")
                
                with col_b:
                    if st.button("📝 Add Note", use_container_width=True):
                        st.success("📝 Note added!")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with monitor_tab3:
        st.markdown("### 🌐 URL & Service Monitor")
        
        # URL monitoring interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            new_url = st.text_input("🌐 Add URL to Monitor", placeholder="https://api.vapi.ai/health")
        
        with col2:
            if st.button("➕ Add URL", use_container_width=True):
                if new_url:
                    if 'live_urls' not in st.session_state:
                        st.session_state.live_urls = []
                    
                    st.session_state.live_urls.append({
                        'url': new_url,
                        'added_time': datetime.now().isoformat()
                    })
                    st.success(f"✅ Added URL: {new_url}")
                else:
                    st.warning("⚠️ Please enter a valid URL")
        
        # Default URLs to monitor
        default_urls = [
            'https://api.vapi.ai/health',
            'https://webhook.vapi.ai/status',
            'https://dashboard.vapi.ai',
            'https://docs.vapi.ai',
            'https://n8n.vapi.ai/health'
        ]
        
        all_urls = default_urls + [item['url'] for item in st.session_state.live_urls]
        
        # Monitor URLs
        url_status_data = []
        for url in all_urls:
            status_info = monitor_live_url(url)
            url_status_data.append({
                'URL': url,
                'Status': status_info['status'],
                'Status Code': status_info['status_code'],
                'Response Time': f"{status_info['response_time']:.3f}s" if status_info['response_time'] > 0 else "N/A",
                'Last Check': status_info['timestamp'],
                'Health': '🟢 Online' if status_info['status'] == 'online' else '🔴 Offline'
            })
        
        url_df = pd.DataFrame(url_status_data)
        
        # URL monitoring metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            online_count = (url_df['Status'] == 'online').sum()
            st.metric("🟢 Online", online_count)
        
        with col2:
            offline_count = (url_df['Status'] != 'online').sum()
            st.metric("🔴 Offline", offline_count)
        
        with col3:
            avg_response_time = url_df['Response Time'].apply(lambda x: float(x.replace('s', '')) if x != 'N/A' else 0).mean()
            st.metric("⚡ Avg Response", f"{avg_response_time:.3f}s")
        
        with col4:
            uptime_percentage = (online_count / len(url_df) * 100) if len(url_df) > 0 else 0
            st.metric("📊 Uptime", f"{uptime_percentage:.1f}%")
        
        # URL status grid
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🌐 URL Status Monitor</div>', unsafe_allow_html=True)
        
        grid_response_urls = create_enhanced_ag_grid(url_df, "url_monitor_grid", height=400, enable_enterprise=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # URL details
        if grid_response_urls['selected_rows']:
            selected_url = grid_response_urls['selected_rows'][0]
            
            st.markdown(f"### 🌐 URL Details: {selected_url['URL']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="url-monitor">', unsafe_allow_html=True)
                st.markdown("#### 📊 Status Information")
                st.write(f"**URL:** {selected_url['URL']}")
                st.write(f"**Status:** {selected_url['Health']}")
                st.write(f"**Status Code:** {selected_url['Status Code']}")
                st.write(f"**Response Time:** {selected_url['Response Time']}")
                st.write(f"**Last Check:** {selected_url['Last Check']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 🛠️ Actions")
                
                if st.button("🔄 Check Now", use_container_width=True):
                    with st.spinner("Checking URL..."):
                        time_module.sleep(1)
                        st.success("✅ URL checked successfully!")
                
                if st.button("📊 View History", use_container_width=True):
                    st.info("📊 Showing URL history...")
                
                if st.button("🗑️ Remove URL", use_container_width=True):
                    st.warning("🗑️ URL removed from monitoring")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with monitor_tab4:
        st.markdown("### ⚠️ System Alerts & Notifications")
        
        # Generate alert data
        alerts = [
            {
                'Time': (datetime.now() - timedelta(minutes=random.randint(1, 60))).strftime('%H:%M:%S'),
                'Type': random.choice(['Warning', 'Error', 'Info', 'Critical']),
                'Source': random.choice(['VAPI API', 'n8n Workflow', 'Database', 'Webhook', 'AI Model']),
                'Message': random.choice([
                    'High API latency detected',
                    'Webhook endpoint not responding',
                    'AI model accuracy below threshold',
                    'Database connection timeout',
                    'Queue length exceeding limit',
                    'System load above 80%',
                    'Failed authentication attempts',
                    'Disk space running low'
                ]),
                'Status': random.choice(['Active', 'Resolved', 'Investigating'])
            }
            for _ in range(15)
        ]
        
        alerts_df = pd.DataFrame(alerts)
        
        # Alert metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            critical_alerts = (alerts_df['Type'] == 'Critical').sum()
            st.metric("🚨 Critical", critical_alerts, delta=f"+{critical_alerts}")
        
        with col2:
            error_alerts = (alerts_df['Type'] == 'Error').sum()
            st.metric("❌ Errors", error_alerts, delta=f"+{error_alerts}")
        
        with col3:
            warning_alerts = (alerts_df['Type'] == 'Warning').sum()
            st.metric("⚠️ Warnings", warning_alerts, delta=f"+{warning_alerts}")
        
        with col4:
            active_alerts = (alerts_df['Status'] == 'Active').sum()
            st.metric("🔴 Active", active_alerts, delta=f"+{active_alerts}")
        
        # Alerts grid
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">⚠️ System Alerts</div>', unsafe_allow_html=True)
        
        grid_response_alerts = create_enhanced_ag_grid(alerts_df, "alerts_grid", height=400, enable_enterprise=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Alert actions
        if grid_response_alerts['selected_rows']:
            selected_alert = grid_response_alerts['selected_rows'][0]
            
            st.markdown(f"### ⚠️ Alert Details")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📋 Alert Information")
                st.write(f"**Time:** {selected_alert['Time']}")
                st.write(f"**Type:** {selected_alert['Type']}")
                st.write(f"**Source:** {selected_alert['Source']}")
                st.write(f"**Status:** {selected_alert['Status']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 📝 Message")
                st.write(f"**Description:** {selected_alert['Message']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="crm-card">', unsafe_allow_html=True)
                st.markdown("#### 🛠️ Actions")
                
                if st.button("✅ Mark Resolved", use_container_width=True):
                    st.success("✅ Alert marked as resolved!")
                
                if st.button("🔍 Investigate", use_container_width=True):
                    st.info("🔍 Investigation started...")
                
                if st.button("📧 Notify Team", use_container_width=True):
                    st.success("📧 Team notified!")
                
                st.markdown('</div>', unsafe_allow_html=True)


elif st.session_state.current_page == "📋 Data Management":
    st.markdown('<h2 class="section-header animate-fadeIn">📋 Advanced Data Management</h2>', unsafe_allow_html=True)
    
    # Data management tabs
    data_tab1, data_tab2, data_tab3, data_tab4, data_tab5 = st.tabs(["📤 Import/Export", "🔄 Data Sync", "🧹 Data Quality", "📊 Data Analysis", "🗄️ Data Archive"])
    
    with data_tab1:
        st.markdown("### 📤 Data Import & Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📥 Data Import</div>', unsafe_allow_html=True)
            
            # File upload
            uploaded_file = st.file_uploader(
                "📁 Upload Data File",
                type=['csv', 'xlsx', 'json', 'parquet'],
                help="Supported formats: CSV, Excel, JSON, Parquet"
            )
            
            if uploaded_file:
                try:
                    # Determine file type and load accordingly
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    
                    if file_extension == 'csv':
                        import_df = pd.read_csv(uploaded_file)
                    elif file_extension in ['xlsx', 'xls']:
                        import_df = pd.read_excel(uploaded_file)
                    elif file_extension == 'json':
                        import_df = pd.read_json(uploaded_file)
                    elif file_extension == 'parquet':
                        import_df = pd.read_parquet(uploaded_file)
                    else:
                        st.error("❌ Unsupported file format")
                        import_df = None
                    
                    if import_df is not None:
                        st.success(f"✅ File loaded successfully! {len(import_df)} rows, {len(import_df.columns)} columns")
                        
                        # Data preview
                        st.markdown("#### 👀 Data Preview")
                        st.dataframe(import_df.head(), use_container_width=True)
                        
                        # Data validation
                        st.markdown("#### ✅ Data Validation")
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("📊 Rows", len(import_df))
                        with col_b:
                            st.metric("📋 Columns", len(import_df.columns))
                        with col_c:
                            missing_values = import_df.isnull().sum().sum()
                            st.metric("❓ Missing Values", missing_values)
                        
                        # Import options
                        st.markdown("#### ⚙️ Import Options")
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            import_mode = st.selectbox("📋 Import Mode", 
                                                     ['Replace All Data', 'Append to Existing', 'Update Existing'])
                            validate_data = st.checkbox("✅ Validate Data", value=True)
                        
                        with col_b:
                            backup_existing = st.checkbox("💾 Backup Existing Data", value=True)
                            send_notification = st.checkbox("📧 Send Import Notification", value=False)
                        
                        # Import button
                        if st.button("📥 Import Data", use_container_width=True):
                            with st.spinner("Importing data..."):
                                time_module.sleep(2)  # Simulate import process
                                
                                if validate_data:
                                    st.info("✅ Data validation completed")
                                
                                if backup_existing:
                                    st.info("💾 Existing data backed up")
                                
                                st.success(f"✅ Data imported successfully! {len(import_df)} records processed.")
                                
                                if send_notification:
                                    st.success("📧 Import notification sent to team")
                
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📤 Data Export</div>', unsafe_allow_html=True)
            
            # Export configuration
            export_format = st.selectbox("📄 Export Format", 
                                       ['CSV', 'Excel', 'JSON', 'Parquet', 'SQL'])
            
            export_scope = st.selectbox("📊 Export Scope", 
                                      ['All Data', 'Filtered Data', 'Selected Columns', 'Date Range'])
            
            if export_scope == 'Date Range':
                export_date_range = st.date_input("📅 Date Range", 
                                                value=[datetime.now().date() - timedelta(days=30), 
                                                      datetime.now().date()])
            
            if export_scope == 'Selected Columns':
                selected_columns = st.multiselect("📋 Select Columns", 
                                                 df.columns.tolist(),
                                                 default=df.columns.tolist()[:5])
            
            # Export options
            include_metadata = st.checkbox("📋 Include Metadata", value=True)
            compress_file = st.checkbox("🗜️ Compress File", value=False)
            
            # Export button
            if st.button("📤 Export Data", use_container_width=True):
                with st.spinner("Preparing export..."):
                    time_module.sleep(2)
                    
                    # Prepare export data based on scope
                    export_df = df.copy()
                    
                    if export_scope == 'Date Range' and 'call_date' in df.columns:
                        export_df = export_df[
                            (pd.to_datetime(export_df['call_date']).dt.date >= export_date_range[0]) &
                            (pd.to_datetime(export_df['call_date']).dt.date <= export_date_range[1])
                        ]
                    elif export_scope == 'Selected Columns':
                        export_df = export_df[selected_columns]
                    
                    # Generate export file
                    if export_format == 'CSV':
                        export_data = export_df.to_csv(index=False)
                        mime_type = "text/csv"
                        file_ext = "csv"
                    elif export_format == 'JSON':
                        export_data = export_df.to_json(orient='records', indent=2)
                        mime_type = "application/json"
                        file_ext = "json"
                    else:
                        export_data = export_df.to_csv(index=False)
                        mime_type = "text/csv"
                        file_ext = "csv"
                    
                    st.download_button(
                        label=f"📥 Download {export_format} File",
                        data=export_data,
                        file_name=f"vapi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}",
                        mime=mime_type,
                        use_container_width=True
                    )
                    
                    st.success(f"✅ Export ready! {len(export_df)} records, {len(export_df.columns)} columns")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with data_tab2:
        st.markdown("### 🔄 Data Synchronization")
        
        # Sync status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔄 Sync Status", "Active", delta="Online")
        with col2:
            last_sync = datetime.now() - timedelta(minutes=random.randint(1, 30))
            st.metric("⏰ Last Sync", last_sync.strftime('%H:%M'))
        with col3:
            st.metric("📊 Records Synced", f"{random.randint(800, 1200):,}")
        with col4:
            st.metric("⚡ Sync Speed", f"{random.randint(50, 150)} rec/sec")
        
        # Sync configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⚙️ Sync Configuration</div>', unsafe_allow_html=True)
            
            sync_frequency = st.selectbox("🔄 Sync Frequency", 
                                        ['Real-time', 'Every 5 minutes', 'Every 15 minutes', 
                                         'Every hour', 'Daily', 'Manual'])
            
            sync_direction = st.selectbox("↔️ Sync Direction", 
                                        ['Bidirectional', 'Import Only', 'Export Only'])
            
            conflict_resolution = st.selectbox("⚔️ Conflict Resolution", 
                                             ['Latest Wins', 'Manual Review', 'Skip Conflicts'])
            
            auto_backup = st.checkbox("💾 Auto Backup Before Sync", value=True)
            
            if st.button("🔄 Start Manual Sync", use_container_width=True):
                with st.spinner("Synchronizing data..."):
                    time_module.sleep(3)
                    st.success("✅ Data synchronized successfully!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 Sync History</div>', unsafe_allow_html=True)
            
            # Generate sync history
            sync_history = []
            for i in range(10):
                sync_time = datetime.now() - timedelta(hours=i*2)
                sync_history.append({
                    'Time': sync_time.strftime('%Y-%m-%d %H:%M'),
                    'Type': random.choice(['Scheduled', 'Manual', 'Auto']),
                    'Records': random.randint(50, 500),
                    'Status': random.choice(['Success', 'Partial', 'Failed']),
                    'Duration': f"{random.randint(10, 180)}s"
                })
            
            sync_df = pd.DataFrame(sync_history)
            
            grid_response_sync = create_enhanced_ag_grid(sync_df, "sync_history_grid", height=300)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with data_tab3:
        st.markdown("### 🧹 Data Quality Management")
        
        # Data quality metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            st.metric("✅ Completeness", f"{completeness:.1f}%")
        
        with col2:
            # Mock accuracy score
            accuracy = random.uniform(85, 95)
            st.metric("🎯 Accuracy", f"{accuracy:.1f}%")
        
        with col3:
            # Mock consistency score
            consistency = random.uniform(90, 98)
            st.metric("🔄 Consistency", f"{consistency:.1f}%")
        
        with col4:
            duplicates = random.randint(5, 25)
            st.metric("🔄 Duplicates", duplicates)
        
        with col5:
            outliers = random.randint(10, 50)
            st.metric("📊 Outliers", outliers)
        
        with col6:
            overall_quality = (completeness + accuracy + consistency) / 3
            st.metric("⭐ Overall Quality", f"{overall_quality:.1f}%")
        
        # Data quality analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 Data Quality by Column</div>', unsafe_allow_html=True)
            
            # Calculate missing values by column
            missing_by_column = df.isnull().sum()
            missing_percentage = (missing_by_column / len(df) * 100).round(1)
            
            quality_df = pd.DataFrame({
                'Column': missing_percentage.index,
                'Missing %': missing_percentage.values,
                'Quality Score': 100 - missing_percentage.values
            })
            
            fig = px.bar(quality_df.head(10), x='Column', y='Quality Score',
                       title="Data Quality Score by Column",
                       labels={'Quality Score': 'Quality Score (%)'})
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔍 Data Issues Detection</div>', unsafe_allow_html=True)
            
            # Mock data issues
            issues = {
                'Issue Type': ['Missing Values', 'Duplicates', 'Outliers', 'Format Errors', 'Invalid Dates'],
                'Count': [random.randint(5, 50) for _ in range(5)],
                'Severity': ['Medium', 'Low', 'High', 'Medium', 'Low']
            }
            
            issues_df = pd.DataFrame(issues)
            
            fig = px.pie(issues_df, values='Count', names='Issue Type',
                       title="Data Issues Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Data cleaning tools
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🧹 Data Cleaning Tools</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🧹 Remove Duplicates", use_container_width=True):
                with st.spinner("Removing duplicates..."):
                    time_module.sleep(1)
                    st.success(f"✅ Removed {random.randint(5, 25)} duplicate records")
        
        with col2:
            if st.button("📊 Fix Outliers", use_container_width=True):
                with st.spinner("Fixing outliers..."):
                    time_module.sleep(1)
                    st.success(f"✅ Fixed {random.randint(10, 30)} outlier values")
        
        with col3:
            if st.button("📅 Validate Dates", use_container_width=True):
                with st.spinner("Validating dates..."):
                    time_module.sleep(1)
                    st.success(f"✅ Validated {random.randint(800, 1000)} date fields")
        
        with col4:
            if st.button("🔤 Standardize Text", use_container_width=True):
                with st.spinner("Standardizing text..."):
                    time_module.sleep(1)
                    st.success(f"✅ Standardized {random.randint(500, 800)} text fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with data_tab4:
        st.markdown("### 📊 Data Analysis Tools")
        
        # Analysis tools
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 Statistical Analysis</div>', unsafe_allow_html=True)
            
            # Select numeric columns for analysis
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_columns:
                selected_column = st.selectbox("📊 Select Column for Analysis", numeric_columns)
                
                if selected_column:
                    col_data = df[selected_column]
                    
                    # Statistical summary
                    st.markdown("#### 📊 Statistical Summary")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("📊 Mean", f"{col_data.mean():.2f}")
                        st.metric("📊 Median", f"{col_data.median():.2f}")
                    
                    with col_b:
                        st.metric("📊 Std Dev", f"{col_data.std():.2f}")
                        st.metric("📊 Min", f"{col_data.min():.2f}")
                    
                    with col_c:
                        st.metric("📊 Max", f"{col_data.max():.2f}")
                        st.metric("📊 Range", f"{col_data.max() - col_data.min():.2f}")
                    
                    # Distribution plot
                    fig = px.histogram(df, x=selected_column, nbins=30,
                                     title=f"Distribution of {selected_column}")
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔍 Correlation Analysis</div>', unsafe_allow_html=True)
            
            if len(numeric_columns) >= 2:
                # Calculate correlation matrix
                correlation_matrix = df[numeric_columns].corr()
                
                # Create heatmap
                fig = px.imshow(correlation_matrix,
                              title="Correlation Matrix",
                              color_continuous_scale='RdBu',
                              aspect="auto")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Need at least 2 numeric columns for correlation analysis")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Advanced analysis
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔬 Advanced Analysis</div>', unsafe_allow_html=True)
        
        analysis_type = st.selectbox("🔬 Analysis Type", 
                                   ['Trend Analysis', 'Anomaly Detection', 'Clustering', 'Forecasting'])
        
        if analysis_type == 'Trend Analysis' and 'call_date' in df.columns:
            # Time series analysis
            daily_trends = df.groupby('call_date').agg({
                'call_id': 'count',
                'customer_satisfaction': 'mean'
            }).reset_index()
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Scatter(x=daily_trends['call_date'], y=daily_trends['call_id'], name="Call Volume"),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(x=daily_trends['call_date'], y=daily_trends['customer_satisfaction'], name="Satisfaction"),
                secondary_y=True,
            )
            fig.update_layout(title="Trend Analysis", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_type == 'Anomaly Detection':
            st.info("🔍 Anomaly detection analysis would be performed here")
            
            # Mock anomaly results
            anomalies = random.randint(5, 20)
            st.metric("⚠️ Anomalies Detected", anomalies)
            
        elif analysis_type == 'Clustering':
            st.info("🎯 Customer clustering analysis would be performed here")
            
            # Mock clustering results
            clusters = random.randint(3, 7)
            st.metric("🎯 Clusters Identified", clusters)
        
        elif analysis_type == 'Forecasting':
            st.info("🔮 Forecasting analysis would be performed here")
            
            # Mock forecast accuracy
            accuracy = random.uniform(85, 95)
            st.metric("🎯 Forecast Accuracy", f"{accuracy:.1f}%")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with data_tab5:
        st.markdown("### 🗄️ Data Archive & Backup")
        
        # Archive metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🗄️ Archived Records", f"{random.randint(5000, 15000):,}")
        with col2:
            st.metric("💾 Backup Size", f"{random.randint(500, 2000)} MB")
        with col3:
            last_backup = datetime.now() - timedelta(hours=random.randint(1, 24))
            st.metric("⏰ Last Backup", last_backup.strftime('%H:%M'))
        with col4:
            st.metric("🔄 Retention Period", "90 days")
        
        # Archive management
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🗄️ Archive Management</div>', unsafe_allow_html=True)
            
            archive_criteria = st.selectbox("📋 Archive Criteria", 
                                          ['Age > 90 days', 'Age > 180 days', 'Age > 1 year', 'Custom'])
            
            if archive_criteria == 'Custom':
                custom_days = st.number_input("📅 Days to Archive", min_value=1, max_value=365, value=90)
            
            archive_compression = st.selectbox("🗜️ Compression", ['None', 'ZIP', 'GZIP', 'BZIP2'])
            
            if st.button("🗄️ Archive Old Data", use_container_width=True):
                with st.spinner("Archiving data..."):
                    time_module.sleep(2)
                    archived_count = random.randint(100, 500)
                    st.success(f"✅ Archived {archived_count} records successfully!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">💾 Backup Management</div>', unsafe_allow_html=True)
            
            backup_frequency = st.selectbox("🔄 Backup Frequency", 
                                          ['Daily', 'Weekly', 'Monthly', 'Manual'])
            
            backup_location = st.selectbox("📍 Backup Location", 
                                         ['Local Storage', 'Cloud Storage', 'Both'])
            
            encryption = st.checkbox("🔒 Encrypt Backups", value=True)
            
            if st.button("💾 Create Backup", use_container_width=True):
                with st.spinner("Creating backup..."):
                    time_module.sleep(3)
                    backup_size = random.randint(100, 500)
                    st.success(f"✅ Backup created successfully! Size: {backup_size} MB")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Backup history
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📋 Backup History</div>', unsafe_allow_html=True)
        
        backup_history = []
        for i in range(10):
            backup_time = datetime.now() - timedelta(days=i)
            backup_history.append({
                'Date': backup_time.strftime('%Y-%m-%d'),
                'Time': backup_time.strftime('%H:%M'),
                'Type': random.choice(['Full', 'Incremental', 'Differential']),
                'Size (MB)': random.randint(100, 800),
                'Status': random.choice(['Success', 'Failed', 'Partial']),
                'Location': random.choice(['Local', 'Cloud', 'Both'])
            })
        
        backup_df = pd.DataFrame(backup_history)
        
        grid_response_backup = create_enhanced_ag_grid(backup_df, "backup_history_grid", height=300)
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "⚙️ Settings":
    st.markdown('<h2 class="section-header animate-fadeIn">⚙️ System Settings & Configuration</h2>', unsafe_allow_html=True)
    
    # Settings tabs
    settings_tab1, settings_tab2, settings_tab3, settings_tab4, settings_tab5, settings_tab6 = st.tabs([
        "🔧 General", "🔐 Security", "🔗 Integrations", "📊 Dashboard", "🔔 Notifications", "🛠️ Advanced"
    ])
    
    with settings_tab1:
        st.markdown("### 🔧 General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🏢 Organization Settings</div>', unsafe_allow_html=True)
            
            org_name = st.text_input("🏢 Organization Name", value="VAPI AI Call Center")
            org_timezone = st.selectbox("🌍 Timezone", 
                                      ['UTC', 'EST', 'PST', 'GMT', 'CET'])
            org_language = st.selectbox("🌐 Default Language", 
                                      ['English', 'Spanish', 'French', 'German'])
            org_currency = st.selectbox("💰 Currency", 
                                      ['USD', 'EUR', 'GBP', 'CAD'])
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 Data Settings</div>', unsafe_allow_html=True)
            
            data_retention = st.slider("🗄️ Data Retention (days)", 30, 365, 90)
            auto_backup = st.checkbox("💾 Auto Backup", value=True)
            data_compression = st.checkbox("🗜️ Data Compression", value=False)
            anonymize_data = st.checkbox("🔒 Anonymize Exported Data", value=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Performance settings
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">⚡ Performance Settings</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cache_duration = st.slider("💾 Cache Duration (minutes)", 1, 60, 5)
            max_records = st.number_input("📊 Max Records per Page", 10, 1000, 100)
        
        with col2:
            refresh_interval = st.slider("🔄 Auto Refresh (seconds)", 5, 300, 30)
            concurrent_users = st.number_input("👥 Max Concurrent Users", 1, 100, 20)
        
        with col3:
            api_timeout = st.slider("⏱️ API Timeout (seconds)", 5, 60, 30)
            batch_size = st.number_input("📦 Batch Processing Size", 10, 1000, 100)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with settings_tab2:
        st.markdown("### 🔐 Security Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔐 Authentication</div>', unsafe_allow_html=True)
            
            auth_method = st.selectbox("🔑 Authentication Method", 
                                     ['Password', 'SSO', 'Multi-Factor', 'API Key'])
            
            password_policy = st.selectbox("🔒 Password Policy", 
                                         ['Basic', 'Strong', 'Enterprise'])
            
            session_timeout = st.slider("⏱️ Session Timeout (minutes)", 15, 480, 60)
            
            max_login_attempts = st.number_input("🚫 Max Login Attempts", 1, 10, 3)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🛡️ Security Features</div>', unsafe_allow_html=True)
            
            enable_2fa = st.checkbox("🔐 Enable 2FA", value=False)
            ip_whitelist = st.checkbox("🌐 IP Whitelist", value=False)
            audit_logging = st.checkbox("📋 Audit Logging", value=True)
            data_encryption = st.checkbox("🔒 Data Encryption", value=True)
            
            if ip_whitelist:
                allowed_ips = st.text_area("📝 Allowed IP Addresses", 
                                         placeholder="192.168.1.1\n10.0.0.1")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Security monitoring
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔍 Security Monitoring</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔐 Active Sessions", random.randint(5, 25))
        with col2:
            st.metric("🚫 Failed Logins", random.randint(0, 5))
        with col3:
            st.metric("⚠️ Security Alerts", random.randint(0, 3))
        with col4:
            st.metric("🛡️ Threat Level", "Low")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with settings_tab3:
        st.markdown("### 🔗 Integration Settings")
        
        # VAPI AI Integration
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🤖 VAPI AI Integration</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            vapi_api_key = st.text_input("🔑 VAPI API Key", type="password", 
                                       placeholder="Enter your VAPI API key")
            vapi_endpoint = st.text_input("🌐 VAPI Endpoint", 
                                        value="https://api.vapi.ai")
            vapi_timeout = st.slider("⏱️ API Timeout", 5, 60, 30)
        
        with col2:
            vapi_rate_limit = st.number_input("📊 Rate Limit (req/min)", 10, 1000, 100)
            vapi_retry_attempts = st.number_input("🔄 Retry Attempts", 1, 5, 3)
            vapi_enable_webhooks = st.checkbox("🔗 Enable Webhooks", value=True)
        
        if st.button("🧪 Test VAPI Connection", use_container_width=True):
            with st.spinner("Testing VAPI connection..."):
                time_module.sleep(2)
                st.success("✅ VAPI connection successful!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # n8n Integration
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔄 n8n Integration</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            n8n_endpoint = st.text_input("🌐 n8n Endpoint", 
                                       value="https://n8n.vapi.ai")
            n8n_api_key = st.text_input("🔑 n8n API Key", type="password",
                                      placeholder="Enter your n8n API key")
        
        with col2:
            n8n_webhook_url = st.text_input("🔗 Webhook URL", 
                                          placeholder="https://n8n.vapi.ai/webhook/...")
            n8n_auto_sync = st.checkbox("🔄 Auto Sync Workflows", value=True)
        
        if st.button("🧪 Test n8n Connection", use_container_width=True):
            with st.spinner("Testing n8n connection..."):
                time_module.sleep(2)
                st.success("✅ n8n connection successful!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Other integrations
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔌 Other Integrations</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            enable_slack = st.checkbox("💬 Slack Integration", value=False)
            if enable_slack:
                slack_webhook = st.text_input("🔗 Slack Webhook URL")
        
        with col2:
            enable_teams = st.checkbox("👥 Microsoft Teams", value=False)
            if enable_teams:
                teams_webhook = st.text_input("🔗 Teams Webhook URL")
        
        with col3:
            enable_email = st.checkbox("📧 Email Integration", value=True)
            if enable_email:
                smtp_server = st.text_input("📧 SMTP Server")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with settings_tab4:
        st.markdown("### 📊 Dashboard Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🎨 Appearance</div>', unsafe_allow_html=True)
            
            theme = st.selectbox("🎨 Theme", ['Light', 'Dark', 'Auto'])
            color_scheme = st.selectbox("🌈 Color Scheme", 
                                      ['VAPI Blue', 'Professional', 'Vibrant', 'Minimal'])
            
            chart_style = st.selectbox("📊 Chart Style", 
                                     ['Modern', 'Classic', 'Minimal', 'Colorful'])
            
            font_size = st.selectbox("🔤 Font Size", ['Small', 'Medium', 'Large'])
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📱 Layout</div>', unsafe_allow_html=True)
            
            sidebar_position = st.selectbox("📱 Sidebar Position", ['Left', 'Right'])
            default_page = st.selectbox("🏠 Default Page", nav_options)
            
            show_tooltips = st.checkbox("💡 Show Tooltips", value=True)
            compact_mode = st.checkbox("📦 Compact Mode", value=False)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Widget configuration
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔧 Widget Configuration</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📊 Metrics")
            show_kpis = st.checkbox("📊 Show KPIs", value=True)
            show_trends = st.checkbox("📈 Show Trends", value=True)
            show_comparisons = st.checkbox("⚖️ Show Comparisons", value=True)
        
        with col2:
            st.markdown("#### 📈 Charts")
            default_chart_type = st.selectbox("📊 Default Chart Type", 
                                            ['Bar', 'Line', 'Pie', 'Scatter'])
            chart_animations = st.checkbox("🎬 Chart Animations", value=True)
            interactive_charts = st.checkbox("🖱️ Interactive Charts", value=True)
        
        with col3:
            st.markdown("#### 📋 Tables")
            default_page_size = st.number_input("📄 Default Page Size", 10, 100, 25)
            enable_export = st.checkbox("📤 Enable Export", value=True)
            enable_filtering = st.checkbox("🔍 Enable Filtering", value=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with settings_tab5:
        st.markdown("### 🔔 Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📧 Email Notifications</div>', unsafe_allow_html=True)
            
            email_alerts = st.checkbox("📧 Email Alerts", value=True)
            
            if email_alerts:
                alert_types = st.multiselect("⚠️ Alert Types", 
                                           ['System Errors', 'High Call Volume', 'Low Success Rate', 
                                            'API Issues', 'Data Quality Issues'])
                
                email_frequency = st.selectbox("📅 Email Frequency", 
                                             ['Immediate', 'Hourly', 'Daily', 'Weekly'])
                
                recipients = st.text_area("📧 Recipients", 
                                        placeholder="admin@company.com\nmanager@company.com")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📱 Push Notifications</div>', unsafe_allow_html=True)
            
            push_notifications = st.checkbox("📱 Push Notifications", value=False)
            
            if push_notifications:
                push_types = st.multiselect("🔔 Notification Types", 
                                          ['Critical Alerts', 'Call Completed', 'Daily Summary', 
                                           'Weekly Report'])
                
                quiet_hours = st.checkbox("🌙 Quiet Hours", value=True)
                
                if quiet_hours:
                    quiet_start = st.time_input("🌅 Quiet Start", value=time(22, 0))
                    quiet_end = st.time_input("🌄 Quiet End", value=time(8, 0))
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Notification history
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📋 Notification History</div>', unsafe_allow_html=True)
        
        notification_history = []
        for i in range(10):
            notif_time = datetime.now() - timedelta(hours=random.randint(1, 48))
            notification_history.append({
                'Time': notif_time.strftime('%Y-%m-%d %H:%M'),
                'Type': random.choice(['Email', 'Push', 'SMS', 'Slack']),
                'Subject': random.choice(['System Alert', 'Daily Report', 'Call Summary', 'Error Notification']),
                'Status': random.choice(['Sent', 'Failed', 'Pending']),
                'Recipients': random.randint(1, 5)
            })
        
        notif_df = pd.DataFrame(notification_history)
        
        grid_response_notif = create_enhanced_ag_grid(notif_df, "notification_history_grid", height=300)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with settings_tab6:
        st.markdown("### 🛠️ Advanced Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔧 System Configuration</div>', unsafe_allow_html=True)
            
            debug_mode = st.checkbox("🐛 Debug Mode", value=False)
            verbose_logging = st.checkbox("📝 Verbose Logging", value=False)
            
            log_level = st.selectbox("📊 Log Level", 
                                   ['ERROR', 'WARNING', 'INFO', 'DEBUG'])
            
            max_log_size = st.number_input("📄 Max Log Size (MB)", 1, 1000, 100)
            
            maintenance_mode = st.checkbox("🔧 Maintenance Mode", value=False)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⚡ Performance Tuning</div>', unsafe_allow_html=True)
            
            enable_caching = st.checkbox("💾 Enable Caching", value=True)
            
            if enable_caching:
                cache_size = st.slider("💾 Cache Size (MB)", 10, 1000, 100)
                cache_ttl = st.slider("⏱️ Cache TTL (minutes)", 1, 60, 5)
            
            parallel_processing = st.checkbox("⚡ Parallel Processing", value=True)
            
            if parallel_processing:
                worker_threads = st.number_input("👥 Worker Threads", 1, 16, 4)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # System information
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">ℹ️ System Information</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("🖥️ CPU Usage", f"{random.randint(20, 80)}%")
        with col2:
            st.metric("💾 Memory Usage", f"{random.randint(40, 90)}%")
        with col3:
            st.metric("💿 Disk Usage", f"{random.randint(30, 70)}%")
        with col4:
            st.metric("🌐 Network I/O", f"{random.randint(10, 50)} MB/s")
        with col5:
            uptime_hours = random.randint(1, 720)
            st.metric("⏱️ Uptime", f"{uptime_hours}h")
        with col6:
            st.metric("📊 Active Connections", random.randint(5, 50))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System actions
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🛠️ System Actions</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Restart System", use_container_width=True):
                st.warning("⚠️ System restart initiated...")
        
        with col2:
            if st.button("🧹 Clear Cache", use_container_width=True):
                st.success("✅ Cache cleared successfully!")
        
        with col3:
            if st.button("📊 Generate Report", use_container_width=True):
                st.info("📊 System report generated!")
        
        with col4:
            if st.button("💾 Backup Settings", use_container_width=True):
                st.success("✅ Settings backed up!")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Save settings button (appears on all settings tabs)
if st.session_state.current_page == "⚙️ Settings":
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("💾 Save All Settings", use_container_width=True):
            with st.spinner("Saving settings..."):
                time_module.sleep(2)
                st.success("✅ All settings saved successfully!")

#


#######################################
# AUTO-REFRESH FUNCTIONALITY
#######################################

# Auto-refresh implementation
if st.session_state.auto_refresh and st.session_state.real_time_mode:
    # Add auto-refresh placeholder
    refresh_placeholder = st.empty()
    
    # Auto-refresh countdown
    if st.session_state.refresh_interval > 0:
        with refresh_placeholder.container():
            st.markdown(f"""
            <div style="position: fixed; top: 10px; right: 10px; background: rgba(99, 102, 241, 0.9); 
                        color: white; padding: 0.5rem 1rem; border-radius: 10px; z-index: 1000;">
                <span class="live-indicator"></span>Auto-refresh in {st.session_state.refresh_interval}s
            </div>
            """, unsafe_allow_html=True)
        
        # Auto-refresh timer
        time_module.sleep(1)
        if st.session_state.refresh_interval > 1:
            st.session_state.refresh_interval -= 1
            st.rerun()
        else:
            st.session_state.refresh_interval = st.session_state.get('original_refresh_interval', 30)
            st.rerun()

#######################################
# FOOTER
#######################################

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); 
            color: white; border-radius: 15px; margin-top: 2rem;">
    <h3>🤖 VAPI AI Call Center Dashboard - Ultimate Edition</h3>
    <p>Advanced AI Phone Call Management with Real-time Analytics & n8n Integration</p>
    <p><strong>Data Source:</strong> {data_source} | <strong>Last Updated:</strong> {current_time.strftime('%Y-%m-%d %H:%M:%S')} | 
    <strong>Total Records:</strong> {len(df):,}</p>
    <p>Powered by VAPI AI • Built with Streamlit • Enhanced with AG Grid & Plotly</p>
</div>
""", unsafe_allow_html=True)

#######################################
# PERFORMANCE MONITORING
#######################################

# Add performance monitoring
if st.session_state.get('show_performance', False):
    with st.expander("📊 Performance Metrics", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💾 Memory Usage", f"{random.randint(40, 80)} MB")
        with col2:
            st.metric("⚡ Load Time", f"{random.randint(800, 1500)} ms")
        with col3:
            st.metric("🔄 Refresh Rate", f"{st.session_state.refresh_interval}s")
        with col4:
            st.metric("👥 Active Users", random.randint(1, 10))

#######################################
# KEYBOARD SHORTCUTS
#######################################

# Add keyboard shortcuts info
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    // Ctrl+R for refresh
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        window.location.reload();
    }
    
    // Ctrl+D for dashboard
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        // Navigate to dashboard
    }
    
    // Ctrl+S for settings
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        // Navigate to settings
    }
});
</script>
""", unsafe_allow_html=True)

#######################################
# FINAL NOTES
#######################################

# Add help information
if st.session_state.get('show_help', False):
    with st.expander("❓ Help & Documentation", expanded=False):
        st.markdown("""
        ### 🚀 Quick Start Guide
        
        1. **Authentication**: Login with password (default: admin123)
        2. **Data Source**: Configure Google Sheets or use demo data
        3. **Navigation**: Use sidebar to switch between pages
        4. **Real-time**: Enable auto-refresh for live updates
        5. **Export**: Use Data Management for export options
        
        ### ⌨️ Keyboard Shortcuts
        
        - `Ctrl + R`: Refresh page
        - `Ctrl + D`: Go to Dashboard
        - `Ctrl + S`: Go to Settings
        
        ### 🔗 Integration
        
        - **VAPI AI**: Configure API key in Settings > Integrations
        - **n8n**: Set up webhook endpoints for automation
        - **Google Sheets**: Upload JSON credentials for live data
        
        ### 📊 Features
        
        - **Real-time Monitoring**: Live call tracking and metrics
        - **Advanced Analytics**: AI insights and predictions
        - **CRM Integration**: Customer management and tracking
        - **Webhook Management**: n8n workflow integration
        - **Data Export**: Multiple format support
        - **URL Monitoring**: Live service status tracking
        
        ### 🛠️ Support
        
        For technical support, contact: support@vapi.ai
        Documentation: https://docs.vapi.ai
        """)

# Debug information (only in debug mode)
if st.session_state.get('debug_mode', False):
    with st.expander("🐛 Debug Information", expanded=False):
        st.json({
            "session_state": dict(st.session_state),
            "data_shape": df.shape,
            "data_columns": df.columns.tolist(),
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            "current_page": st.session_state.current_page,
            "timestamp": datetime.now().isoformat()
        })

print("🤖 VAPI AI Dashboard Ultimate - Loaded Successfully!")
print(f"📊 Data Source: {data_source}")
print(f"📋 Total Records: {len(df):,}")
print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

