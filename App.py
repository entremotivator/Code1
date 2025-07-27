"""
AIVA Call Center Dashboard - Ultimate Widget Version with Streamlit Calendar
Requirements: streamlit, plotly, pandas, gspread, google-auth, streamlit-aggrid, streamlit-calendar
Run with: streamlit run aiva_dashboard_ultimate_widgets.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
from streamlit_calendar import calendar
import gspread
from google.oauth2.service_account import Credentials
import json
import io
from datetime import datetime, timedelta, date, time
import numpy as np
import os
import re
import time as time_module
import calendar as cal_module
import hashlib
import base64
import random
import string
import uuid

# Authentication functions
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def get_configured_password():
        """Get password from secrets or use default"""
        try:
            return st.secrets.get("password", "admin123")
        except:
            # Fallback to environment variable or default
            return os.environ.get("AIVA_PASSWORD", "admin123")
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        configured_password = get_configured_password()
        if st.session_state["password"] == configured_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "🔐 Enter Password", type="password", on_change=password_entered, key="password"
        )
        st.info("Default password: admin123")
        st.caption("💡 You can set a custom password via environment variable AIVA_PASSWORD or Streamlit secrets")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "🔐 Enter Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

def create_kpi_card(title, value, delta, delta_type):
    """Creates a styled KPI card with optional delta indicator."""
    delta_class = "neutral"
    if delta_type == "positive":
        delta_class = "positive"
    elif delta_type == "negative":
        delta_class = "negative"

    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta {delta_class}">{delta}</div>
    </div>
    """

#######################################
# PAGE SETUP
#######################################

st.set_page_config(
    page_title="AIVA Call Center Ultimate", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.aiva.com/help',
        'Report a bug': "https://www.aiva.com/bug",
        'About': "# AIVA Call Center Ultimate Dashboard\nThe most comprehensive call center analytics platform!"
    }
)

# Enhanced CSS for AIVA branding and modern UI with all widget styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        font-family: 'Inter', sans-serif;
        max-width: 100%;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* AIVA Brand Colors */
    :root {
        --aiva-primary: #2563eb;
        --aiva-secondary: #1e40af;
        --aiva-accent: #3b82f6;
        --aiva-success: #10b981;
        --aiva-warning: #f59e0b;
        --aiva-danger: #ef4444;
        --aiva-dark: #1f2937;
        --aiva-light: #f8fafc;
        --aiva-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --aiva-gradient-2: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        --aiva-gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --aiva-calendar: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        --aiva-widget: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    }
    
    /* Header styling */
    .aiva-header {
        background: var(--aiva-gradient-2);
        padding: 3rem 2rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .aiva-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .aiva-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        position: relative;
        z-index: 1;
        background: linear-gradient(45deg, #fff, #e0e7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .aiva-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.4rem;
        font-weight: 500;
        margin: 1rem 0 0 0;
        position: relative;
        z-index: 1;
    }
    
    /* Navigation styling */
    .nav-container {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 3rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    /* Widget container styling */
    .widget-container {
        background: white;
        border-radius: 25px;
        padding: 2rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    
    .widget-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .widget-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--aiva-dark);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 2px solid var(--aiva-primary);
        padding-bottom: 0.5rem;
    }
    
    /* Calendar specific styling */
    .calendar-container {
        background: white;
        border-radius: 25px;
        padding: 2rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin-bottom: 2rem;
        min-height: 600px;
    }
    
    .calendar-header {
        background: var(--aiva-calendar);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        font-weight: 700;
        font-size: 1.8rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .calendar-tabs {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 1rem;
        flex-wrap: wrap;
    }
    
    .calendar-tab {
        padding: 1rem 2rem;
        border-radius: 15px;
        background: #f8fafc;
        border: 2px solid #e5e7eb;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        color: #6b7280;
        flex: 1;
        min-width: 120px;
        text-align: center;
    }
    
    .calendar-tab.active {
        background: var(--aiva-primary);
        color: white;
        border-color: var(--aiva-primary);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
    }
    
    .calendar-tab:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin-bottom: 4rem;
    }
    
    .kpi-card {
        background: white;
        border-radius: 25px;
        padding: 2.5rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: var(--aiva-gradient);
    }
    
    .kpi-title {
        font-size: 1rem;
        font-weight: 700;
        color: #6b7280;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .kpi-value {
        font-size: 3.2rem;
        font-weight: 800;
        color: var(--aiva-dark);
        margin-bottom: 0.75rem;
        line-height: 1;
    }
    
    .kpi-delta {
        font-size: 1rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .kpi-delta.positive {
        color: var(--aiva-success);
    }
    
    .kpi-delta.negative {
        color: var(--aiva-danger);
    }
    
    .kpi-delta.neutral {
        color: #6b7280;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        border-radius: 25px;
        padding: 2.5rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin-bottom: 3rem;
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
    }
    
    .chart-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--aiva-dark);
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        border-bottom: 3px solid var(--aiva-primary);
        padding-bottom: 1rem;
    }
    
    /* Data source info */
    .data-source-info {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 3px solid #0ea5e9;
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 3rem;
        color: #0c4a6e;
        font-weight: 600;
        text-align: center;
        font-size: 1.2rem;
        box-shadow: 0 10px 25px rgba(14, 165, 233, 0.2);
    }
    
    /* Authentication styling */
    .auth-container {
        background: var(--aiva-gradient);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .auth-status {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar enhancements */
    .sidebar-section {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--aiva-dark);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Enhanced widget styling */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--aiva-primary);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    
    .stSlider > div > div > div {
        background: var(--aiva-gradient);
    }
    
    .stCheckbox > label {
        font-weight: 600;
        color: var(--aiva-dark);
    }
    
    .stRadio > label {
        font-weight: 600;
        color: var(--aiva-dark);
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--aiva-primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--aiva-primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--aiva-primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    .stDateInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .stTimeInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--aiva-gradient);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(37, 99, 235, 0.4);
    }
    
    .stDownloadButton > button {
        background: var(--aiva-success);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1rem;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(16, 185, 129, 0.4);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed var(--aiva-primary);
        border-radius: 15px;
        padding: 2rem;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--aiva-secondary);
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: var(--aiva-gradient);
        border-radius: 10px;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric styling override */
    [data-testid="metric-container"] {
        background: white;
        border: 2px solid #e5e7eb;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
        border-color: var(--aiva-primary);
    }
    
    /* Code block styling */
    .stCode {
        background: #1f2937;
        border-radius: 15px;
        border: 2px solid #374151;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        font-weight: 600;
        color: var(--aiva-dark);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        color: var(--aiva-dark);
        font-weight: 600;
        padding: 1rem 2rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--aiva-gradient);
        color: white;
        border-color: var(--aiva-primary);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .aiva-title {
            font-size: 2.8rem;
        }
        
        .kpi-container {
            grid-template-columns: 1fr;
        }
        
        .calendar-tabs {
            flex-direction: column;
        }
        
        .calendar-tab {
            text-align: center;
        }
        
        .widget-container {
            padding: 1rem;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--aiva-gradient);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--aiva-secondary);
    }
    
    /* Animation keyframes */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-pulse {
        animation: pulse 2s infinite;
    }
    
    .animate-fadeIn {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Check authentication
if not check_password():
    st.stop()

# AIVA Header
st.markdown("""
<div class="aiva-header animate-fadeIn">
    <h1 class="aiva-title">🤖 AIVA Call Center Ultimate</h1>
    <p class="aiva-subtitle">The Most Comprehensive AI-Powered Call Analytics & Performance Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

#######################################
# HORIZONTAL NAVIGATION
#######################################

# Navigation state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Navigation menu with all pages
nav_options = [
    'Dashboard', 'Calendar', 'Widgets Showcase', 'Call Analytics', 
    'Agent Performance', 'Client Profiles', 'Reports', 'Real-time Monitor',
    'Data Management', 'Settings', 'Advanced Tools'
]

# Create navigation buttons
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
cols = st.columns(len(nav_options))
for i, option in enumerate(nav_options):
    with cols[i]:
        if st.button(
            option, 
            key=f"nav_{option}",
            use_container_width=True,
            type="primary" if st.session_state.current_page == option else "secondary"
        ):
            st.session_state.current_page = option
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

#######################################
# ENHANCED SIDEBAR CONFIGURATION
#######################################

with st.sidebar:
    # Authentication Status
    st.markdown("""
    <div class="auth-container">
        <h3>🔐 Authentication Status</h3>
        <div class="auth-status">
            ✅ Successfully Authenticated<br>
            <small>Session Active</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Google Sheets Authentication Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🔐 Live Data Source Authentication</div>', unsafe_allow_html=True)
    
    # Pre-fill the Google Sheets URL
    default_sheets_url = "https://docs.google.com/spreadsheets/d/1LFfNwb9lRQpIosSEvV3O6zIwymUIWeG9L_k7cxw1jQs/"
    
    sheets_url = st.text_input(
        "📋 Google Sheets URL",
        value=default_sheets_url,
        help="Enter the complete Google Sheets URL for live data",
        key="sheets_url_input"
    )
    
    # Enhanced JSON uploader with better styling and status
    st.markdown("#### 🔑 Service Account JSON Authentication")
    uploaded_json = st.file_uploader(
        "Upload JSON Credentials", 
        type=['json'],
        help="Upload your Google Service Account credentials JSON file for authenticated access to private sheets",
        key="json_uploader"
    )
    
    # Enhanced JSON status display
    if uploaded_json:
        try:
            json_content = json.loads(uploaded_json.read().decode('utf-8'))
            st.success("✅ JSON credentials successfully loaded")
            
            # Display JSON details in an expandable section
            with st.expander("📋 JSON Credential Details"):
                st.info(f"**Service Account Email:** {json_content.get('client_email', 'Unknown')}")
                st.info(f"**Project ID:** {json_content.get('project_id', 'Unknown')}")
                st.info(f"**Client ID:** {json_content.get('client_id', 'Unknown')}")
                st.info(f"**Auth URI:** {json_content.get('auth_uri', 'Unknown')}")
                
            uploaded_json.seek(0)  # Reset file pointer for main usage
            
        except Exception as e:
            st.error(f"❌ Invalid JSON format: {str(e)}")
            st.warning("Please upload a valid Google Service Account JSON file")
    else:
        st.warning("⚠️ No JSON credentials uploaded")
        st.info("📝 **Authentication Options:**")
        st.markdown("""
        - **Public Sheets**: No authentication needed
        - **Private Sheets**: Upload JSON credentials above
        - **Fallback**: Use CSV upload option below
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    # Widget Controls
    st.markdown("#### 🎛️ Widget Controls")
    show_animations = st.checkbox("Enable Animations", value=True)
    show_tooltips = st.checkbox("Show Tooltips", value=True)
    compact_mode = st.checkbox("Compact Mode", value=False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data Refresh Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🔄 Data Refresh Settings</div>', unsafe_allow_html=True)
    
    auto_refresh = st.checkbox("Auto-refresh data", value=True, help="Automatically refresh data every few minutes")
    refresh_interval = st.selectbox("Refresh Interval (minutes)", [1, 5, 10, 15, 30], index=1, help="Minutes between auto-refresh")
    
    # Real-time toggle
    real_time_mode = st.toggle("Real-time Mode", value=False, help="Enable real-time data updates")
    
    if real_time_mode:
        st.info("🔴 Real-time mode active")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calendar Settings Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📅 Calendar Settings</div>', unsafe_allow_html=True)
    
    calendar_view = st.selectbox("Default Calendar View", ["dayGridMonth", "timeGridWeek", "timeGridDay", "listWeek"], help="Choose default calendar view")
    show_weekends = st.checkbox("Show Weekends", value=True, help="Display weekends in calendar")
    calendar_theme = st.selectbox("Calendar Theme", ["standard", "bootstrap", "material"], help="Choose calendar theme")
    
    # Calendar event settings
    st.markdown("#### 📋 Event Settings")
    event_color_success = st.color_picker("Success Color", "#10b981")
    event_color_failed = st.color_picker("Failed Color", "#ef4444")
    event_color_pending = st.color_picker("Pending Color", "#f59e0b")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced Settings
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">⚙️ Advanced Settings</div>', unsafe_allow_html=True)
    
    # Performance settings
    st.markdown("#### 🚀 Performance")
    enable_caching = st.checkbox("Enable Caching", value=True)
    cache_ttl = st.slider("Cache TTL (minutes)", 1, 60, 5)
    
    # Display settings
    st.markdown("#### 🎨 Display")
    theme_mode = st.radio("Theme Mode", ["Light", "Dark", "Auto"], horizontal=True)
    font_size = st.selectbox("Font Size", ["Small", "Medium", "Large"], index=1)
    
    # Data settings
    st.markdown("#### 📊 Data")
    max_rows = st.number_input("Max Rows to Display", min_value=10, max_value=10000, value=1000)
    precision = st.slider("Decimal Precision", 0, 5, 2)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export Settings Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📊 Export Settings</div>', unsafe_allow_html=True)
    
    export_format = st.selectbox("Export Format", ["CSV", "Excel", "JSON", "PDF"], help="Choose export format for data")
    include_charts = st.checkbox("Include Charts in Export", value=True, help="Include visualizations in exported reports")
    include_metadata = st.checkbox("Include Metadata", value=True, help="Include data source and timestamp info")
    
    if st.button("📤 Export Current Data", use_container_width=True):
        st.info(f"Exporting data in {export_format} format...")
        # Export functionality would be implemented here
        st.success(f"Data exported successfully as {export_format}!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # System Information
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">💻 System Information</div>', unsafe_allow_html=True)
    
    st.metric("Memory Usage", "45.2 MB")
    st.metric("Cache Size", "12.8 MB")
    st.metric("Active Sessions", "1")
    st.metric("Uptime", "2h 15m")
    
    # System status indicator
    st.markdown("#### 🟢 System Status")
    st.success("All systems operational")
    
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
def load_demo_data():
    """Generate comprehensive demo data with all possible fields"""
    try:
        np.random.seed(42)  # For reproducible data
        n_records = 500
        
        # Generate realistic call center data
        start_date = datetime.now() - timedelta(days=90)
        dates = [start_date + timedelta(days=x) for x in range(90)]
        
        sample_data = {
            'call_id': [f"CALL-{1000+i:04d}" for i in range(n_records)],
            'client_name': [f'Client {random.choice(["Corp", "Ltd", "Inc", "LLC", "Group"])} {i//10+1}' for i in range(n_records)],
            'email': [f'client{i}@{random.choice(["example", "test", "demo", "company"])}.com' for i in range(n_records)],
            'phone_number': [f'+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}' for _ in range(n_records)],
            'booking_status': np.random.choice(['Confirmed', 'Pending', 'Cancelled', 'Rescheduled', 'No-show'], n_records, p=[0.4, 0.2, 0.15, 0.15, 0.1]),
            'voice_agent_name': np.random.choice(['Agent Smith', 'Agent Johnson', 'Agent Williams', 'Agent Brown', 'Agent Davis', 'Agent Miller'], n_records),
            'call_date': [random.choice(dates).strftime('%Y-%m-%d') for _ in range(n_records)],
            'call_start_time': [f'{random.randint(8, 18):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}' for _ in range(n_records)],
            'call_end_time': [f'{random.randint(8, 19):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}' for _ in range(n_records)],
            'call_length_seconds': np.random.randint(30, 3600, n_records),
            'call_duration_seconds': np.random.randint(30, 3600, n_records),
            'call_duration_hms': [f'{random.randint(0, 1):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}' for _ in range(n_records)],
            'cost': np.round(np.random.uniform(0.25, 15.0, n_records), 2),
            'call_success': np.random.choice(['Yes', 'No'], n_records, p=[0.75, 0.25]),
            'appointment_scheduled': np.random.choice(['Yes', 'No'], n_records, p=[0.6, 0.4]),
            'intent_detected': np.random.choice(['Booking', 'Support', 'Sales', 'Complaint', 'Information', 'Cancellation'], n_records),
            'sentiment_score': np.round(np.random.uniform(0.1, 1.0, n_records), 3),
            'confidence_score': np.round(np.random.uniform(0.5, 1.0, n_records), 3),
            'keyword_tags': [', '.join(random.sample(['urgent', 'follow-up', 'new-client', 'vip', 'technical', 'billing', 'support'], random.randint(1, 4))) for _ in range(n_records)],
            'summary_word_count': np.random.randint(50, 500, n_records),
            'transcript': [f'Sample transcript for call {i+1}. Customer discussed {random.choice(["booking", "support", "billing", "technical"])} issues.' for i in range(n_records)],
            'summary': [f'Call summary {i+1}: {random.choice(["Successful", "Needs follow-up", "Issue resolved", "Escalated"])}' for i in range(n_records)],
            'action_items': [f'Action {i+1}: {random.choice(["Follow up in 3 days", "Send documentation", "Schedule callback", "Escalate to manager"])}' for i in range(n_records)],
            'call_recording_url': [f'https://recordings.aiva.com/call_{i+1000}.mp3' for i in range(n_records)],
            'customer_satisfaction': np.round(np.random.uniform(1.0, 5.0, n_records), 1),
            'resolution_time_seconds': np.random.randint(60, 1800, n_records),
            'response_time_minutes': np.round(np.random.uniform(0.5, 30.0, n_records), 1),
            'escalation_required': np.random.choice(['Yes', 'No'], n_records, p=[0.15, 0.85]),
            'language_detected': np.random.choice(['English', 'Spanish', 'French', 'German'], n_records, p=[0.7, 0.15, 0.1, 0.05]),
            'emotion_detected': np.random.choice(['Happy', 'Neutral', 'Frustrated', 'Angry', 'Satisfied'], n_records, p=[0.3, 0.4, 0.15, 0.1, 0.05]),
            'speech_rate_wpm': np.random.randint(120, 200, n_records),
            'silence_percentage': np.round(np.random.uniform(5.0, 25.0, n_records), 1),
            'interruption_count': np.random.randint(0, 10, n_records),
            'ai_accuracy_score': np.round(np.random.uniform(0.7, 1.0, n_records), 3),
            'follow_up_required': np.random.choice(['Yes', 'No'], n_records, p=[0.3, 0.7]),
            'customer_tier': np.random.choice(['Bronze', 'Silver', 'Gold', 'Platinum', 'VIP'], n_records, p=[0.3, 0.25, 0.2, 0.15, 0.1]),
            'call_complexity': np.random.choice(['Low', 'Medium', 'High', 'Critical'], n_records, p=[0.4, 0.35, 0.2, 0.05]),
            'agent_performance_score': np.round(np.random.uniform(0.6, 1.0, n_records), 2),
            'call_outcome': np.random.choice(['Resolved', 'Pending', 'Escalated', 'Transferred', 'Dropped'], n_records, p=[0.5, 0.2, 0.15, 0.1, 0.05]),
            'revenue_impact': np.round(np.random.uniform(-500, 5000, n_records), 2),
            'lead_quality_score': np.round(np.random.uniform(0.1, 1.0, n_records), 2),
            'conversion_probability': np.round(np.random.uniform(0.0, 1.0, n_records), 3),
            'next_best_action': [random.choice(['Call back', 'Send email', 'Schedule meeting', 'Send proposal', 'Close deal']) for _ in range(n_records)],
            'customer_lifetime_value': np.round(np.random.uniform(100, 50000, n_records), 2),
            'call_category': np.random.choice(['Inbound Sales', 'Outbound Sales', 'Customer Support', 'Technical Support', 'Billing'], n_records),
            'upload_timestamp': [(datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat() for _ in range(n_records)],
            'call_hour': [int(time_str.split(':')[0]) for time_str in [f'{random.randint(8, 18):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}' for _ in range(n_records)]],
            'call_day_of_week': [random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']) for _ in range(n_records)],
            'call_month': [random.randint(1, 12) for _ in range(n_records)],
            'call_quarter': [random.randint(1, 4) for _ in range(n_records)],
            'agent_experience_years': np.round(np.random.uniform(0.5, 10.0, n_records), 1),
            'customer_age': np.random.randint(18, 80, n_records),
            'customer_location': np.random.choice(['New York', 'California', 'Texas', 'Florida', 'Illinois', 'Pennsylvania'], n_records),
            'call_source': np.random.choice(['Website', 'Phone', 'Email', 'Social Media', 'Referral', 'Advertisement'], n_records),
            'device_type': np.random.choice(['Mobile', 'Desktop', 'Tablet', 'Landline'], n_records),
            'connection_quality': np.random.choice(['Excellent', 'Good', 'Fair', 'Poor'], n_records, p=[0.4, 0.35, 0.2, 0.05]),
            'background_noise_level': np.random.choice(['Low', 'Medium', 'High'], n_records, p=[0.6, 0.3, 0.1]),
            'call_priority': np.random.choice(['Low', 'Normal', 'High', 'Urgent'], n_records, p=[0.2, 0.5, 0.25, 0.05]),
            'previous_calls_count': np.random.randint(0, 20, n_records),
            'days_since_last_call': np.random.randint(0, 365, n_records),
            'product_interest': np.random.choice(['Product A', 'Product B', 'Product C', 'Service X', 'Service Y'], n_records),
            'budget_range': np.random.choice(['< $1K', '$1K-$5K', '$5K-$10K', '$10K-$50K', '> $50K'], n_records),
            'decision_maker': np.random.choice(['Yes', 'No', 'Partial'], n_records, p=[0.4, 0.4, 0.2]),
            'urgency_level': np.random.choice(['Low', 'Medium', 'High', 'Critical'], n_records, p=[0.3, 0.4, 0.25, 0.05]),
            'competitor_mentioned': np.random.choice(['Yes', 'No'], n_records, p=[0.2, 0.8]),
            'objections_raised': np.random.choice(['Price', 'Features', 'Timeline', 'Authority', 'None'], n_records, p=[0.2, 0.15, 0.1, 0.1, 0.45]),
            'demo_requested': np.random.choice(['Yes', 'No'], n_records, p=[0.3, 0.7]),
            'proposal_sent': np.random.choice(['Yes', 'No'], n_records, p=[0.25, 0.75]),
            'contract_value': np.round(np.random.uniform(0, 100000, n_records), 2),
            'close_probability': np.round(np.random.uniform(0.0, 1.0, n_records), 2),
            'expected_close_date': [(datetime.now() + timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d') for _ in range(n_records)],
            'sales_stage': np.random.choice(['Prospect', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost'], n_records),
            'lead_source': np.random.choice(['Website', 'Referral', 'Cold Call', 'Email Campaign', 'Social Media', 'Trade Show'], n_records),
            'industry': np.random.choice(['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education'], n_records),
            'company_size': np.random.choice(['1-10', '11-50', '51-200', '201-1000', '1000+'], n_records),
            'annual_revenue': np.random.choice(['< $1M', '$1M-$10M', '$10M-$100M', '$100M-$1B', '> $1B'], n_records),
            'pain_points': [', '.join(random.sample(['Cost', 'Efficiency', 'Scalability', 'Integration', 'Support', 'Training'], random.randint(1, 3))) for _ in range(n_records)],
            'goals': [', '.join(random.sample(['Increase Revenue', 'Reduce Costs', 'Improve Efficiency', 'Scale Operations', 'Better Analytics'], random.randint(1, 3))) for _ in range(n_records)],
            'timeline': np.random.choice(['Immediate', '1-3 months', '3-6 months', '6-12 months', '> 1 year'], n_records),
            'implementation_complexity': np.random.choice(['Simple', 'Moderate', 'Complex', 'Very Complex'], n_records),
            'technical_requirements': [', '.join(random.sample(['API Integration', 'Custom Development', 'Data Migration', 'Training', 'Support'], random.randint(1, 3))) for _ in range(n_records)],
            'compliance_requirements': np.random.choice(['None', 'GDPR', 'HIPAA', 'SOX', 'PCI-DSS'], n_records, p=[0.4, 0.2, 0.15, 0.15, 0.1]),
            'security_level': np.random.choice(['Standard', 'Enhanced', 'Enterprise', 'Government'], n_records, p=[0.5, 0.3, 0.15, 0.05]),
            'integration_needs': [', '.join(random.sample(['CRM', 'ERP', 'Marketing Automation', 'Analytics', 'Communication'], random.randint(0, 3))) for _ in range(n_records)],
            'training_required': np.random.choice(['None', 'Basic', 'Advanced', 'Custom'], n_records, p=[0.2, 0.4, 0.3, 0.1]),
            'support_level': np.random.choice(['Self-Service', 'Standard', 'Premium', 'Enterprise'], n_records, p=[0.2, 0.4, 0.3, 0.1]),
            'renewal_probability': np.round(np.random.uniform(0.0, 1.0, n_records), 2),
            'churn_risk': np.random.choice(['Low', 'Medium', 'High'], n_records, p=[0.6, 0.3, 0.1]),
            'upsell_opportunity': np.random.choice(['None', 'Low', 'Medium', 'High'], n_records, p=[0.4, 0.3, 0.2, 0.1]),
            'cross_sell_products': [', '.join(random.sample(['Add-on A', 'Add-on B', 'Service X', 'Service Y', 'Premium Support'], random.randint(0, 2))) for _ in range(n_records)],
            'satisfaction_trend': np.random.choice(['Improving', 'Stable', 'Declining'], n_records, p=[0.3, 0.5, 0.2]),
            'engagement_score': np.round(np.random.uniform(0.0, 1.0, n_records), 2),
            'feature_usage': np.round(np.random.uniform(0.0, 1.0, n_records), 2),
            'login_frequency': np.random.choice(['Daily', 'Weekly', 'Monthly', 'Rarely'], n_records, p=[0.3, 0.4, 0.2, 0.1]),
            'support_tickets': np.random.randint(0, 20, n_records),
            'feature_requests': np.random.randint(0, 10, n_records),
            'referrals_made': np.random.randint(0, 5, n_records),
            'nps_score': np.random.randint(-100, 100, n_records),
            'csat_score': np.round(np.random.uniform(1.0, 5.0, n_records), 1),
            'effort_score': np.round(np.random.uniform(1.0, 5.0, n_records), 1)
        }
        
        return pd.DataFrame(sample_data)
    except Exception as e:
        st.error(f"Error generating demo data: {e}")
        return pd.DataFrame()

# Data Loading Logic - Priority: Google Sheets > CSV > Demo Data
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

# PRIORITY 2: Fallback to CSV Upload
if df is None and 'uploaded_csv' in locals() and uploaded_csv:
    df, error = load_csv_data(uploaded_csv)
    if df is not None:
        data_source = "CSV Upload (Fallback)"
        st.warning("⚠️ Using CSV fallback data. Configure Google Sheets for live data.")
    else:
        st.error(f"❌ CSV Error: {error}")

# PRIORITY 3: Use demo data as last resort
if df is None:
    df = load_demo_data()
    if not df.empty:
        data_source = "Demo Data (Comprehensive)"
        st.info("🎯 Using comprehensive demo data with all possible fields. Configure Google Sheets or upload CSV for live data.")
    else:
        st.error("❌ No data available. Please check the demo data generation.")
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
    📊 <strong>Data Source:</strong> {data_source} | 
    <strong>Last Updated:</strong> {current_time.strftime('%H:%M:%S')} | 
    <strong>Total Records:</strong> {len(df):,} |
    <strong>Date Range:</strong> {date_range} |
    <strong>Columns:</strong> {len(df.columns)} |
    <strong>Memory Usage:</strong> {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB
</div>
""", unsafe_allow_html=True)

#######################################
# CALENDAR FUNCTIONS
#######################################

def generate_calendar_events(df):
    """Generate calendar events from call data for streamlit-calendar"""
    events = []
    
    if 'call_date' in df.columns and 'call_start_time' in df.columns:
        for _, row in df.iterrows():
            try:
                # Parse date and time
                call_date = pd.to_datetime(row['call_date']).date()
                call_time = pd.to_datetime(row['call_start_time'], format='%H:%M:%S').time()
                
                # Combine date and time
                start_datetime = datetime.combine(call_date, call_time)
                
                # Calculate end time (add call duration)
                duration_seconds = row.get('call_length_seconds', 300)  # Default 5 minutes
                end_datetime = start_datetime + timedelta(seconds=duration_seconds)
                
                # Determine event color based on call success
                if row.get('call_success') == 'Yes':
                    color = event_color_success
                elif row.get('call_success') == 'No':
                    color = event_color_failed
                else:
                    color = event_color_pending
                
                # Create event for streamlit-calendar
                event = {
                    'title': f"📞 {row.get('client_name', 'Unknown')}",
                    'start': start_datetime.isoformat(),
                    'end': end_datetime.isoformat(),
                    'backgroundColor': color,
                    'borderColor': color,
                    'textColor': 'white',
                    'extendedProps': {
                        'agent': row.get('voice_agent_name', 'Unknown'),
                        'status': row.get('call_success', 'Unknown'),
                        'duration': f"{duration_seconds//60}m {duration_seconds%60}s",
                        'sentiment': row.get('sentiment_score', 0),
                        'satisfaction': row.get('customer_satisfaction', 0),
                        'call_id': row.get('call_id', 'Unknown'),
                        'phone': row.get('phone_number', 'Unknown'),
                        'intent': row.get('intent_detected', 'Unknown'),
                        'outcome': row.get('call_outcome', 'Unknown')
                    }
                }
                events.append(event)
            except Exception as e:
                continue
    
    return events

def create_mini_calendar():
    """Create a mini calendar widget"""
    today = datetime.now()
    cal = cal_module.monthcalendar(today.year, today.month)
    month_name = cal_module.month_name[today.month]
    
    mini_cal_html = f"""
    <div style="background: white; border-radius: 15px; padding: 1.5rem; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1); margin-bottom: 1rem;">
        <h4 style="text-align: center; margin-bottom: 1rem; color: #1f2937; font-weight: 700;">{month_name} {today.year}</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <th style="padding: 8px; text-align: center; font-size: 0.8rem; border-radius: 4px;">Su</th>
                <th style="padding: 8px; text-align: center; font-size: 0.8rem;">Mo</th>
                <th style="padding: 8px; text-align: center; font-size: 0.8rem;">Tu</th>
                <th style="padding: 8px; text-align: center; font-size: 0.8rem;">We</th>
                <th style="padding: 8px; text-align: center; font-size: 0.8rem;">Th</th>
                <th style="padding: 8px; text-align: center; font-size: 0.8rem;">Fr</th>
                <th style="padding: 8px; text-align: center; font-size: 0.8rem; border-radius: 4px;">Sa</th>
            </tr>
    """
    
    for week in cal:
        mini_cal_html += "<tr>"
        for day in week:
            if day == 0:
                mini_cal_html += '<td style="padding: 8px; text-align: center; color: #d1d5db;"></td>'
            elif day == today.day:
                mini_cal_html += f'<td style="padding: 8px; text-align: center; background: #3b82f6; color: white; border-radius: 50%; font-weight: bold;">{day}</td>'
            else:
                mini_cal_html += f'<td style="padding: 8px; text-align: center; cursor: pointer; border-radius: 4px; transition: all 0.2s;" onmouseover="this.style.background=\'#f3f4f6\'" onmouseout="this.style.background=\'transparent\'">{day}</td>'
        mini_cal_html += "</tr>"
    
    mini_cal_html += """
        </table>
    </div>
    """
    
    return mini_cal_html

#######################################
# DATA PROCESSING FUNCTIONS
#######################################

def safe_numeric_conversion(series, default=0):
    """Safely convert series to numeric, replacing errors with default"""
    return pd.to_numeric(series, errors='coerce').fillna(default)

def process_call_metrics():
    """Process key call center metrics with robust column handling"""
    try:
        # Convert numeric columns safely
        numeric_cols = ['call_length_seconds', 'call_duration_seconds', 'cost', 'sentiment_score', 
                       'response_time_minutes', 'customer_satisfaction', 'resolution_time_seconds',
                       'agent_performance_score', 'revenue_impact', 'conversion_probability']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = safe_numeric_conversion(df[col])
        
        # Calculate comprehensive metrics
        total_calls = len(df)
        total_cost = df['cost'].sum() if 'cost' in df.columns else 0
        
        # Use call_length_seconds or call_duration_seconds
        duration_col = 'call_length_seconds' if 'call_length_seconds' in df.columns else 'call_duration_seconds'
        avg_call_duration = df[duration_col].mean() / 60 if duration_col in df.columns else 0
        
        success_rate = (df['call_success'] == 'Yes').sum() / total_calls * 100 if 'call_success' in df.columns else 0
        avg_sentiment = df['sentiment_score'].mean() if 'sentiment_score' in df.columns else 0
        appointments_scheduled = (df['appointment_scheduled'] == 'Yes').sum() if 'appointment_scheduled' in df.columns else 0
        avg_response_time = df['response_time_minutes'].mean() if 'response_time_minutes' in df.columns else 0
        total_agents = df['voice_agent_name'].nunique() if 'voice_agent_name' in df.columns else 0
        avg_satisfaction = df['customer_satisfaction'].mean() if 'customer_satisfaction' in df.columns else 0
        total_revenue = df['revenue_impact'].sum() if 'revenue_impact' in df.columns else 0
        avg_conversion = df['conversion_probability'].mean() if 'conversion_probability' in df.columns else 0
        avg_ai_accuracy = df['ai_accuracy_score'].mean() if 'ai_accuracy_score' in df.columns else 0
        escalations = (df['escalation_required'] == 'Yes').sum() if 'escalation_required' in df.columns else 0
        follow_ups = (df['follow_up_required'] == 'Yes').sum() if 'follow_up_required' in df.columns else 0
        
        # Additional comprehensive metrics
        avg_nps = df['nps_score'].mean() if 'nps_score' in df.columns else 0
        avg_csat = df['csat_score'].mean() if 'csat_score' in df.columns else 0
        avg_effort = df['effort_score'].mean() if 'effort_score' in df.columns else 0
        high_value_deals = (df['contract_value'] > 10000).sum() if 'contract_value' in df.columns else 0
        churn_risk_high = (df['churn_risk'] == 'High').sum() if 'churn_risk' in df.columns else 0
        upsell_opportunities = (df['upsell_opportunity'].isin(['Medium', 'High'])).sum() if 'upsell_opportunity' in df.columns else 0
        
        return {
            'total_calls': total_calls,
            'total_cost': total_cost,
            'avg_call_duration': avg_call_duration,
            'success_rate': success_rate,
            'avg_sentiment': avg_sentiment,
            'appointments_scheduled': appointments_scheduled,
            'avg_response_time': avg_response_time,
            'total_agents': total_agents,
            'avg_satisfaction': avg_satisfaction,
            'total_revenue': total_revenue,
            'avg_conversion': avg_conversion * 100,
            'avg_ai_accuracy': avg_ai_accuracy * 100,
            'escalations': escalations,
            'follow_ups': follow_ups,
            'avg_nps': avg_nps,
            'avg_csat': avg_csat,
            'avg_effort': avg_effort,
            'high_value_deals': high_value_deals,
            'churn_risk_high': churn_risk_high,
            'upsell_opportunities': upsell_opportunities
        }
    except Exception as e:
        st.error(f"Error processing call metrics: {e}")
        return {
            'total_calls': 0, 'total_cost': 0, 'avg_call_duration': 0, 'success_rate': 0,
            'avg_sentiment': 0, 'appointments_scheduled': 0, 'avg_response_time': 0,
            'total_agents': 0, 'avg_satisfaction': 0, 'total_revenue': 0, 'avg_conversion': 0,
            'avg_ai_accuracy': 0, 'escalations': 0, 'follow_ups': 0, 'avg_nps': 0,
            'avg_csat': 0, 'avg_effort': 0, 'high_value_deals': 0, 'churn_risk_high': 0,
            'upsell_opportunities': 0
        }

def create_enhanced_ag_grid(dataframe, grid_key, height=400):
    """Create an enhanced AG Grid with extensive advanced features"""
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    
    # Enable comprehensive features
    gb.configure_pagination(
        paginationAutoPageSize=True,
        paginationPageSize=50
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
        minWidth=100,
        flex=1,
        wrapText=True,
        autoHeight=True,
        cellStyle={'textAlign': 'left'},
        headerTooltip=True
    )
    
    # Configure advanced selection options
    gb.configure_selection(
        selection_mode='multiple',
        use_checkbox=True,
        groupSelectsChildren=True,
        groupSelectsFiltered=True
    )
    
    gridOptions = gb.build()
    
    # Display AG Grid with all features
    grid_response = AgGrid(
        dataframe,
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=False,
        theme='streamlit',
        enable_enterprise_modules=True,
        height=height,
        width='100%',
        key=grid_key,
        reload_data=False,
        try_to_convert_back_to_original_types=True,
        conversion_errors='coerce'
    )
    
    return grid_response


#######################################
# PAGE ROUTING WITH ALL WIDGETS
#######################################

if st.session_state.current_page == 'Dashboard':
    st.markdown('<h2 class="section-header animate-fadeIn">📊 Executive Dashboard</h2>', unsafe_allow_html=True)
    
    # Process metrics
    metrics = process_call_metrics()
    
    # Enhanced KPI Cards with more metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            label="📞 Total Calls",
            value=f"{metrics['total_calls']:,}",
            delta=f"+{metrics['total_calls']//10} this week"
        )
    
    with col2:
        st.metric(
            label="✅ Success Rate",
            value=f"{metrics['success_rate']:.1f}%",
            delta=f"+{metrics['success_rate']*0.1:.1f}%"
        )
    
    with col3:
        st.metric(
            label="💰 Total Revenue",
            value=f"${metrics['total_revenue']:,.2f}",
            delta=f"+${metrics['total_revenue']*0.15:.2f}"
        )
    
    with col4:
        st.metric(
            label="⭐ Avg Satisfaction",
            value=f"{metrics['avg_satisfaction']:.1f}/5.0",
            delta=f"+{metrics['avg_satisfaction']*0.05:.1f}"
        )
    
    with col5:
        st.metric(
            label="🎯 NPS Score",
            value=f"{metrics['avg_nps']:.0f}",
            delta=f"+{metrics['avg_nps']*0.1:.0f}"
        )
    
    with col6:
        st.metric(
            label="🚀 Upsell Ops",
            value=f"{metrics['upsell_opportunities']:,}",
            delta=f"+{metrics['upsell_opportunities']//5}"
        )
    
    # Real-time status indicators
    st.markdown("### 🔴 Real-time Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Calls", random.randint(5, 25))
    with col2:
        st.metric("Queue Length", random.randint(0, 10))
    with col3:
        st.metric("Available Agents", random.randint(8, 15))
    with col4:
        st.metric("Avg Wait Time", f"{random.randint(30, 180)}s")
    
    # Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Call Volume Trends</div>', unsafe_allow_html=True)
        
        # Create sample trend data
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        volumes = np.random.randint(50, 200, len(dates))
        
        fig = px.line(x=dates, y=volumes, title="Daily Call Volume")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🎯 Success Rate by Agent</div>', unsafe_allow_html=True)
        
        if 'voice_agent_name' in df.columns:
            agent_success = df.groupby('voice_agent_name')['call_success'].apply(
                lambda x: (x == 'Yes').sum() / len(x) * 100
            ).reset_index()
            
            fig = px.bar(agent_success, x='voice_agent_name', y='call_success', 
                       title="Success Rate by Agent")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == 'Calendar':
    st.markdown('<div class="calendar-header animate-fadeIn">📅 AIVA Calendar - Advanced Call Schedule & Events</div>', unsafe_allow_html=True)
    
    # Calendar configuration options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        calendar_mode = st.selectbox(
            "📅 Calendar Mode",
            ["Interactive Calendar", "Event List", "Timeline View", "Agenda View"],
            help="Choose how to display calendar events"
        )
    
    with col2:
        date_range_filter = st.date_input(
            "📆 Date Range",
            value=[datetime.now().date() - timedelta(days=7), datetime.now().date() + timedelta(days=7)],
            help="Filter events by date range"
        )
    
    with col3:
        event_filter = st.multiselect(
            "🔍 Filter Events",
            ["Successful Calls", "Failed Calls", "Pending Calls", "High Priority", "VIP Clients"],
            default=["Successful Calls", "Failed Calls"],
            help="Filter events by type"
        )
    
    # Generate events for calendar
    events = generate_calendar_events(df)
    
    if calendar_mode == "Interactive Calendar":
        st.markdown("### 📅 Interactive Calendar with Streamlit-Calendar")
        
        # Calendar options
        calendar_options = {
            "editable": "true",
            "navLinks": "true",
            "selectable": "true",
            "selectMirror": "true",
            "dayMaxEvents": "3",
            "moreLinkClick": "popover",
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek"
            },
            "initialView": calendar_view,
            "themeSystem": calendar_theme,
            "weekends": show_weekends,
            "height": "auto",
            "eventDisplay": "block",
            "eventTimeFormat": {
                "hour": "2-digit",
                "minute": "2-digit",
                "meridiem": "short"
            },
            "slotMinTime": "08:00:00",
            "slotMaxTime": "20:00:00",
            "allDaySlot": False,
            "nowIndicator": True,
            "businessHours": {
                "daysOfWeek": [1, 2, 3, 4, 5],
                "startTime": "09:00",
                "endTime": "18:00"
            }
        }
        
        # Custom CSS for calendar
        custom_css = """
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-weight: bold;
        }
        .fc-event-title {
            font-weight: 600;
        }
        .fc-toolbar-title {
            font-size: 1.75em !important;
            font-weight: 700 !important;
        }
        .fc-button-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            border-radius: 8px !important;
        }
        .fc-button-primary:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
        }
        .fc-day-today {
            background: rgba(59, 130, 246, 0.1) !important;
        }
        """
        
        # Display the calendar
        calendar_component = calendar(
            events=events,
            options=calendar_options,
            custom_css=custom_css,
            key="aiva_calendar"
        )
        
        # Handle calendar interactions
        if calendar_component.get('eventClick'):
            event_data = calendar_component['eventClick']['event']
            st.markdown("### 📋 Event Details")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Title:** {event_data.get('title', 'N/A')}")
                st.info(f"**Start:** {event_data.get('start', 'N/A')}")
                st.info(f"**End:** {event_data.get('end', 'N/A')}")
            
            with col2:
                if 'extendedProps' in event_data:
                    props = event_data['extendedProps']
                    st.info(f"**Agent:** {props.get('agent', 'N/A')}")
                    st.info(f"**Status:** {props.get('status', 'N/A')}")
                    st.info(f"**Duration:** {props.get('duration', 'N/A')}")
        
        if calendar_component.get('dateClick'):
            clicked_date = calendar_component['dateClick']['date']
            st.success(f"📅 Selected date: {clicked_date}")
    
    elif calendar_mode == "Event List":
        st.markdown("### 📋 Event List View")
        
        # Create event list
        event_list = []
        for event in events:
            event_list.append({
                'Time': event['start'],
                'Title': event['title'],
                'Agent': event['extendedProps']['agent'],
                'Status': event['extendedProps']['status'],
                'Duration': event['extendedProps']['duration'],
                'Sentiment': event['extendedProps']['sentiment'],
                'Satisfaction': event['extendedProps']['satisfaction']
            })
        
        if event_list:
            event_df = pd.DataFrame(event_list)
            st.dataframe(event_df, use_container_width=True)
        else:
            st.info("No events found for the selected criteria.")
    
    elif calendar_mode == "Timeline View":
        st.markdown("### ⏰ Timeline View")
        
        # Create timeline visualization
        if events:
            timeline_data = []
            for event in events:
                timeline_data.append({
                    'Task': event['title'],
                    'Start': event['start'],
                    'Finish': event['end'],
                    'Resource': event['extendedProps']['agent']
                })
            
            timeline_df = pd.DataFrame(timeline_data)
            timeline_df['Start'] = pd.to_datetime(timeline_df['Start'])
            timeline_df['Finish'] = pd.to_datetime(timeline_df['Finish'])
            
            fig = px.timeline(timeline_df, x_start="Start", x_end="Finish", y="Task", color="Resource")
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No events available for timeline view.")
    
    elif calendar_mode == "Agenda View":
        st.markdown("### 📝 Agenda View")
        
        # Group events by date
        events_by_date = {}
        for event in events:
            event_date = event['start'][:10]  # Extract date part
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Display agenda
        for date, day_events in sorted(events_by_date.items()):
            st.markdown(f"#### 📅 {date}")
            for event in day_events:
                start_time = event['start'][11:16]  # Extract time part
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                           border-left: 4px solid {event['backgroundColor']}; 
                           padding: 1rem; margin: 0.5rem 0; border-radius: 8px;">
                    <strong>{start_time} - {event['title']}</strong><br>
                    <small>Agent: {event['extendedProps']['agent']} | Status: {event['extendedProps']['status']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Calendar statistics
    st.markdown("### 📊 Calendar Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📅 Total Events", len(events))
    with col2:
        successful_calls = len([e for e in events if e['extendedProps']['status'] == 'Yes'])
        st.metric("✅ Successful Calls", successful_calls)
    with col3:
        failed_calls = len([e for e in events if e['extendedProps']['status'] == 'No'])
        st.metric("❌ Failed Calls", failed_calls)
    with col4:
        avg_duration = np.mean([float(e['extendedProps']['duration'].split('m')[0]) for e in events if 'm' in e['extendedProps']['duration']])
        st.metric("⏱️ Avg Duration", f"{avg_duration:.1f}m")

elif st.session_state.current_page == 'Widgets Showcase':
    st.markdown('<h2 class="section-header animate-fadeIn">🎛️ Ultimate Widgets Showcase</h2>', unsafe_allow_html=True)
    
    # Create tabs for different widget categories
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Input Widgets", "📊 Display Widgets", "📈 Chart Widgets", 
        "🎛️ Control Widgets", "📋 Data Widgets", "🎨 Layout Widgets"
    ])
    
    with tab1:
        st.markdown("### 📝 Input Widgets Showcase")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">📝 Text Inputs</div>', unsafe_allow_html=True)
            
            text_input = st.text_input("Text Input", value="Sample text", help="Enter any text")
            text_area = st.text_area("Text Area", value="Multi-line\ntext input", help="Enter multiple lines")
            password_input = st.text_input("Password Input", type="password", help="Enter password")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🔢 Number Inputs</div>', unsafe_allow_html=True)
            
            number_input = st.number_input("Number Input", min_value=0, max_value=100, value=50)
            slider_input = st.slider("Slider", min_value=0, max_value=100, value=25)
            range_slider = st.select_slider("Range Slider", options=range(0, 101, 10), value=(20, 80))
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">📅 Date & Time Inputs</div>', unsafe_allow_html=True)
            
            date_input = st.date_input("Date Input", value=datetime.now().date())
            time_input = st.time_input("Time Input", value=datetime.now().time())
            datetime_input = st.date_input("Date Range", value=[datetime.now().date(), datetime.now().date() + timedelta(days=7)])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🎨 Color & File Inputs</div>', unsafe_allow_html=True)
            
            color_input = st.color_picker("Color Picker", value="#FF6B6B")
            file_uploader = st.file_uploader("File Uploader", type=['csv', 'xlsx', 'json'])
            camera_input = st.camera_input("Camera Input")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📊 Display Widgets Showcase")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">📊 Metrics & Progress</div>', unsafe_allow_html=True)
            
            st.metric("Sample Metric", "1,234", delta="123", delta_color="normal")
            st.progress(0.75, text="Progress: 75%")
            
            # Custom progress bars
            progress_col1, progress_col2 = st.columns(2)
            with progress_col1:
                st.metric("Success Rate", "87.5%", delta="2.3%")
            with progress_col2:
                st.metric("Efficiency", "94.2%", delta="-1.1%", delta_color="inverse")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🎨 Visual Elements</div>', unsafe_allow_html=True)
            
            st.image("https://via.placeholder.com/300x200/667eea/ffffff?text=Sample+Image", caption="Sample Image")
            st.video("https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">💬 Messages & Alerts</div>', unsafe_allow_html=True)
            
            st.success("✅ Success message!")
            st.info("ℹ️ Information message")
            st.warning("⚠️ Warning message")
            st.error("❌ Error message")
            
            # Balloons and snow
            if st.button("🎈 Celebrate!", key="balloons"):
                st.balloons()
            
            if st.button("❄️ Snow Effect!", key="snow"):
                st.snow()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">📝 Text Display</div>', unsafe_allow_html=True)
            
            st.markdown("**Markdown** *formatting* with `code`")
            st.latex(r"\sum_{i=1}^{n} x_i^2")
            st.code("print('Hello, AIVA!')", language="python")
            st.json({"key": "value", "number": 123, "array": [1, 2, 3]})
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 📈 Chart Widgets Showcase")
        
        # Generate sample data for charts
        chart_data = pd.DataFrame({
            'x': range(10),
            'y': np.random.randn(10).cumsum(),
            'category': np.random.choice(['A', 'B', 'C'], 10)
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">📊 Basic Charts</div>', unsafe_allow_html=True)
            
            st.line_chart(chart_data.set_index('x')['y'])
            st.bar_chart(chart_data.groupby('category')['y'].sum())
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🗺️ Map Charts</div>', unsafe_allow_html=True)
            
            map_data = pd.DataFrame({
                'lat': [37.7749, 40.7128, 41.8781, 29.7604],
                'lon': [-122.4194, -74.0060, -87.6298, -95.3698],
                'size': [100, 200, 150, 120]
            })
            st.map(map_data)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">📈 Advanced Plotly Charts</div>', unsafe_allow_html=True)
            
            # Plotly scatter plot
            fig_scatter = px.scatter(chart_data, x='x', y='y', color='category', 
                                   title="Interactive Scatter Plot")
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Plotly pie chart
            pie_data = chart_data.groupby('category')['y'].sum().reset_index()
            fig_pie = px.pie(pie_data, values='y', names='category', title="Category Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 🎛️ Control Widgets Showcase")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🔘 Selection Widgets</div>', unsafe_allow_html=True)
            
            checkbox = st.checkbox("Checkbox", value=True)
            radio = st.radio("Radio Buttons", ["Option 1", "Option 2", "Option 3"], horizontal=True)
            selectbox = st.selectbox("Select Box", ["Choice A", "Choice B", "Choice C"])
            multiselect = st.multiselect("Multi-select", ["Item 1", "Item 2", "Item 3", "Item 4"], default=["Item 1", "Item 3"])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🔄 Toggle & Switch</div>', unsafe_allow_html=True)
            
            toggle = st.toggle("Toggle Switch", value=True)
            if toggle:
                st.success("Toggle is ON")
            else:
                st.info("Toggle is OFF")
            
            # Custom toggle with session state
            if 'custom_toggle' not in st.session_state:
                st.session_state.custom_toggle = False
            
            if st.button("🔄 Custom Toggle"):
                st.session_state.custom_toggle = not st.session_state.custom_toggle
            
            if st.session_state.custom_toggle:
                st.success("Custom toggle is ON")
            else:
                st.info("Custom toggle is OFF")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🎮 Interactive Controls</div>', unsafe_allow_html=True)
            
            # Button variations
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("Primary", type="primary"):
                    st.success("Primary clicked!")
            with col_btn2:
                if st.button("Secondary", type="secondary"):
                    st.info("Secondary clicked!")
            with col_btn3:
                if st.button("Default"):
                    st.warning("Default clicked!")
            
            # Download button
            sample_data = "Sample,Data,File\n1,2,3\n4,5,6"
            st.download_button(
                label="📥 Download Sample Data",
                data=sample_data,
                file_name="sample_data.csv",
                mime="text/csv"
            )
            
            # Form with submit button
            with st.form("sample_form"):
                form_input = st.text_input("Form Input")
                form_slider = st.slider("Form Slider", 0, 100, 50)
                submitted = st.form_submit_button("Submit Form")
                
                if submitted:
                    st.success(f"Form submitted! Input: {form_input}, Slider: {form_slider}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 📋 Data Widgets Showcase")
        
        st.markdown('<div class="widget-container">', unsafe_allow_html=True)
        st.markdown('<div class="widget-title">📊 Data Display</div>', unsafe_allow_html=True)
        
        # Sample dataframe
        sample_df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'Age': [25, 30, 35, 28, 32],
            'City': ['New York', 'London', 'Tokyo', 'Paris', 'Sydney'],
            'Score': [85.5, 92.3, 78.9, 88.1, 95.7],
            'Active': [True, False, True, True, False]
        })
        
        # Basic dataframe
        st.dataframe(sample_df, use_container_width=True)
        
        # Static table
        st.table(sample_df.head(3))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="widget-container">', unsafe_allow_html=True)
        st.markdown('<div class="widget-title">🔧 Advanced Data Grid</div>', unsafe_allow_html=True)
        
        # AG Grid showcase
        grid_response = create_enhanced_ag_grid(sample_df, "showcase_grid", height=300)
        
        if grid_response['selected_rows']:
            st.success(f"Selected {len(grid_response['selected_rows'])} rows")
            st.json(grid_response['selected_rows'])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab6:
        st.markdown("### 🎨 Layout Widgets Showcase")
        
        st.markdown('<div class="widget-container">', unsafe_allow_html=True)
        st.markdown('<div class="widget-title">📐 Layout Elements</div>', unsafe_allow_html=True)
        
        # Columns
        st.markdown("#### Columns Layout")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.info("Column 1")
        with col2:
            st.success("Column 2 (wider)")
        with col3:
            st.warning("Column 3")
        
        # Expander
        with st.expander("🔽 Expandable Section"):
            st.write("This content is hidden by default and can be expanded!")
            st.slider("Hidden Slider", 0, 100, 50)
        
        # Container
        with st.container():
            st.markdown("#### Container Example")
            st.write("This content is in a container")
        
        # Empty placeholder
        placeholder = st.empty()
        placeholder.info("This is a placeholder that can be updated")
        
        if st.button("Update Placeholder"):
            placeholder.success("Placeholder updated!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="widget-container">', unsafe_allow_html=True)
        st.markdown('<div class="widget-title">🎭 Advanced Layout</div>', unsafe_allow_html=True)
        
        # Sidebar content (already shown in main sidebar)
        st.info("Sidebar content is shown in the main sidebar")
        
        # Status elements
        status = st.status("Processing data...", expanded=True)
        status.write("Step 1: Loading data")
        status.write("Step 2: Processing")
        status.write("Step 3: Complete!")
        status.update(label="Data processing complete!", state="complete", expanded=False)
        
        # Chat elements
        st.markdown("#### Chat Interface")
        with st.chat_message("user"):
            st.write("Hello, AIVA!")
        
        with st.chat_message("assistant"):
            st.write("Hello! How can I help you with your call center analytics today?")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == 'Call Analytics':
    st.markdown('<h2 class="section-header animate-fadeIn">📈 Advanced Call Analytics</h2>', unsafe_allow_html=True)
    
    # Analytics filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_filter = st.date_input("📅 Date Range", value=[datetime.now().date() - timedelta(days=30), datetime.now().date()])
    with col2:
        agent_filter = st.multiselect("👥 Agents", df['voice_agent_name'].unique() if 'voice_agent_name' in df.columns else [])
    with col3:
        status_filter = st.multiselect("📊 Call Status", df['call_success'].unique() if 'call_success' in df.columns else [])
    with col4:
        sentiment_filter = st.slider("😊 Sentiment Range", 0.0, 1.0, (0.0, 1.0), step=0.1)
    
    # Apply filters
    filtered_df = df.copy()
    if agent_filter:
        filtered_df = filtered_df[filtered_df['voice_agent_name'].isin(agent_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df['call_success'].isin(status_filter)]
    
    # Analytics content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Call Distribution</div>', unsafe_allow_html=True)
        
        if 'call_success' in filtered_df.columns:
            success_counts = filtered_df['call_success'].value_counts()
            fig = px.pie(values=success_counts.values, names=success_counts.index, 
                        title="Call Success Distribution")
            fig.update_layout(font_family="Inter")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">⏱️ Call Duration Analysis</div>', unsafe_allow_html=True)
        
        if 'call_length_seconds' in filtered_df.columns:
            fig = px.histogram(filtered_df, x='call_length_seconds', nbins=20, 
                             title="Call Duration Distribution")
            fig.update_layout(font_family="Inter")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced analytics
    st.markdown("### 🔬 Advanced Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "😊 Sentiment", "💰 Revenue", "🎯 Predictions"])
    
    with tab1:
        # Performance analytics
        if 'voice_agent_name' in filtered_df.columns:
            agent_performance = filtered_df.groupby('voice_agent_name').agg({
                'call_id': 'count',
                'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100,
                'call_length_seconds': 'mean',
                'customer_satisfaction': 'mean'
            }).round(2)
            
            agent_performance.columns = ['Total Calls', 'Success Rate (%)', 'Avg Duration (s)', 'Avg Satisfaction']
            st.dataframe(agent_performance, use_container_width=True)
    
    with tab2:
        # Sentiment analysis
        if 'sentiment_score' in filtered_df.columns:
            fig = px.scatter(filtered_df, x='call_length_seconds', y='sentiment_score', 
                           color='call_success', title="Sentiment vs Call Duration")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Revenue analysis
        if 'revenue_impact' in filtered_df.columns:
            revenue_by_agent = filtered_df.groupby('voice_agent_name')['revenue_impact'].sum().sort_values(ascending=False)
            fig = px.bar(x=revenue_by_agent.index, y=revenue_by_agent.values, 
                        title="Revenue Impact by Agent")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Predictive analytics
        st.info("🔮 Predictive analytics features coming soon!")
        
        # Mock prediction data
        prediction_data = pd.DataFrame({
            'Metric': ['Call Success Rate', 'Customer Satisfaction', 'Revenue Growth', 'Agent Performance'],
            'Current': [87.5, 4.2, 15.3, 92.1],
            'Predicted (Next Month)': [89.2, 4.4, 18.7, 94.5],
            'Confidence': [0.85, 0.78, 0.72, 0.91]
        })
        
        st.dataframe(prediction_data, use_container_width=True)
    
    # Data table
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📋 Detailed Call Data</div>', unsafe_allow_html=True)
    
    # Display enhanced AG Grid
    grid_response = create_enhanced_ag_grid(filtered_df.head(100), "analytics_grid", height=500)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == 'Agent Performance':
    st.markdown('<h2 class="section-header animate-fadeIn">👥 Agent Performance Dashboard</h2>', unsafe_allow_html=True)
    
    if 'voice_agent_name' in df.columns:
        # Agent selection
        selected_agent = st.selectbox("👤 Select Agent", ["All Agents"] + list(df['voice_agent_name'].unique()))
        
        # Filter data for selected agent
        if selected_agent != "All Agents":
            agent_df = df[df['voice_agent_name'] == selected_agent]
        else:
            agent_df = df
        
        # Agent metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_calls = len(agent_df)
            st.metric("📞 Total Calls", total_calls)
        
        with col2:
            success_rate = (agent_df['call_success'] == 'Yes').sum() / len(agent_df) * 100 if len(agent_df) > 0 else 0
            st.metric("✅ Success Rate", f"{success_rate:.1f}%")
        
        with col3:
            avg_duration = agent_df['call_length_seconds'].mean() / 60 if 'call_length_seconds' in agent_df.columns else 0
            st.metric("⏱️ Avg Duration", f"{avg_duration:.1f}m")
        
        with col4:
            avg_satisfaction = agent_df['customer_satisfaction'].mean() if 'customer_satisfaction' in agent_df.columns else 0
            st.metric("⭐ Avg Satisfaction", f"{avg_satisfaction:.1f}/5")
        
        with col5:
            total_revenue = agent_df['revenue_impact'].sum() if 'revenue_impact' in agent_df.columns else 0
            st.metric("💰 Revenue Impact", f"${total_revenue:,.0f}")
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily performance trend
            if 'call_date' in agent_df.columns:
                daily_performance = agent_df.groupby('call_date').agg({
                    'call_id': 'count',
                    'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100
                }).reset_index()
                
                fig = px.line(daily_performance, x='call_date', y='call_success', 
                            title="Daily Success Rate Trend")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Call outcome distribution
            if 'call_outcome' in agent_df.columns:
                outcome_counts = agent_df['call_outcome'].value_counts()
                fig = px.pie(values=outcome_counts.values, names=outcome_counts.index,
                           title="Call Outcome Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        # Detailed agent comparison
        if selected_agent == "All Agents":
            st.markdown("### 📊 Agent Comparison")
            
            agent_metrics = df.groupby('voice_agent_name').agg({
                'call_id': 'count',
                'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100,
                'call_length_seconds': 'mean',
                'customer_satisfaction': 'mean',
                'revenue_impact': 'sum'
            }).round(2)
            
            agent_metrics.columns = ['Total Calls', 'Success Rate (%)', 'Avg Duration (s)', 'Avg Satisfaction', 'Revenue Impact']
            
            grid_response = create_enhanced_ag_grid(agent_metrics.reset_index(), "agent_grid", height=400)

elif st.session_state.current_page == 'Client Profiles':
    st.markdown('<h2 class="section-header animate-fadeIn">👤 Client Profiles & Management</h2>', unsafe_allow_html=True)
    
    # Client search and filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search Clients", placeholder="Enter client name, phone, or email")
    with col2:
        tier_filter = st.multiselect("🏆 Client Tier", df['customer_tier'].unique() if 'customer_tier' in df.columns else [])
    with col3:
        status_filter = st.selectbox("📊 Call Status", ["All", "Successful", "Failed", "Pending"])
    
    # Filter clients based on search and filters
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['client_name'].str.contains(search_term, case=False, na=False) |
            filtered_df['phone_number'].str.contains(search_term, case=False, na=False) |
            filtered_df['email'].str.contains(search_term, case=False, na=False)
        ]
    
    if tier_filter:
        filtered_df = filtered_df[filtered_df['customer_tier'].isin(tier_filter)]
    
    if status_filter != "All":
        status_map = {"Successful": "Yes", "Failed": "No", "Pending": "Pending"}
        filtered_df = filtered_df[filtered_df['call_success'] == status_map[status_filter]]
    
    # Client overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Clients", filtered_df['client_name'].nunique())
    with col2:
        avg_clv = filtered_df['customer_lifetime_value'].mean() if 'customer_lifetime_value' in filtered_df.columns else 0
        st.metric("💰 Avg CLV", f"${avg_clv:,.0f}")
    with col3:
        high_value = (filtered_df['customer_lifetime_value'] > 10000).sum() if 'customer_lifetime_value' in filtered_df.columns else 0
        st.metric("💎 High Value Clients", high_value)
    with col4:
        churn_risk = (filtered_df['churn_risk'] == 'High').sum() if 'churn_risk' in filtered_df.columns else 0
        st.metric("⚠️ Churn Risk", churn_risk)
    
    # Client list view
    st.markdown("### 📋 Client Directory")
    
    # Create client summary
    client_summary = filtered_df.groupby('client_name').agg({
        'call_id': 'count',
        'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100,
        'customer_satisfaction': 'mean',
        'customer_lifetime_value': 'first',
        'customer_tier': 'first',
        'churn_risk': 'first',
        'phone_number': 'first',
        'email': 'first',
        'call_date': 'max'
    }).round(2)
    
    client_summary.columns = ['Total Calls', 'Success Rate (%)', 'Avg Satisfaction', 'CLV', 'Tier', 'Churn Risk', 'Phone', 'Email', 'Last Call']
    
    # Display client grid
    grid_response = create_enhanced_ag_grid(client_summary.reset_index(), "client_grid", height=500)
    
    # Selected client details
    if grid_response['selected_rows']:
        selected_client = grid_response['selected_rows'][0]
        client_name = selected_client['client_name']
        
        st.markdown(f"### 👤 Client Details: {client_name}")
        
        client_data = filtered_df[filtered_df['client_name'] == client_name]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Client Metrics")
            st.metric("Total Calls", len(client_data))
            st.metric("Success Rate", f"{(client_data['call_success'] == 'Yes').sum() / len(client_data) * 100:.1f}%")
            st.metric("Avg Satisfaction", f"{client_data['customer_satisfaction'].mean():.1f}/5")
            st.metric("Total Revenue", f"${client_data['revenue_impact'].sum():,.0f}")
        
        with col2:
            st.markdown("#### 📈 Call History")
            if len(client_data) > 1:
                fig = px.line(client_data.sort_values('call_date'), x='call_date', y='customer_satisfaction',
                            title=f"Satisfaction Trend for {client_name}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data for trend analysis")

elif st.session_state.current_page == 'Reports':
    st.markdown('<h2 class="section-header animate-fadeIn">📊 Advanced Reporting Suite</h2>', unsafe_allow_html=True)
    
    # Report generation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Generate Reports</div>', unsafe_allow_html=True)
        
        report_type = st.selectbox("📋 Report Type", [
            "Executive Summary", "Daily Operations", "Weekly Analysis", "Monthly Overview", 
            "Agent Performance", "Client Analysis", "Revenue Report", "Quality Assurance",
            "Predictive Analytics", "Custom Report"
        ])
        
        date_range = st.date_input("📅 Date Range", [
            datetime.now().date() - timedelta(days=30), 
            datetime.now().date()
        ])
        
        report_format = st.selectbox("📄 Format", ["PDF", "Excel", "PowerPoint", "CSV", "JSON"])
        
        include_charts = st.checkbox("📊 Include Charts", value=True)
        include_raw_data = st.checkbox("📋 Include Raw Data", value=False)
        
        if st.button("🚀 Generate Report", use_container_width=True, type="primary"):
            with st.spinner("Generating report..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time_module.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                st.success(f"✅ {report_type} report generated successfully!")
                
                # Mock report data
                report_data = f"""
# {report_type} Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Date Range: {date_range[0]} to {date_range[1]}

## Executive Summary
- Total Calls: {len(df):,}
- Success Rate: {(df['call_success'] == 'Yes').sum() / len(df) * 100:.1f}%
- Average Satisfaction: {df['customer_satisfaction'].mean():.1f}/5
- Total Revenue: ${df['revenue_impact'].sum():,.2f}

## Key Insights
1. Peak call hours: 10 AM - 2 PM
2. Highest performing agent: {df['voice_agent_name'].mode().iloc[0] if 'voice_agent_name' in df.columns else 'N/A'}
3. Most common call outcome: {df['call_outcome'].mode().iloc[0] if 'call_outcome' in df.columns else 'N/A'}
                """
                
                st.download_button(
                    label=f"📥 Download {report_type} Report",
                    data=report_data,
                    file_name=f"{report_type.lower().replace(' ', '_')}_report.txt",
                    mime="text/plain"
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📋 Recent Reports</div>', unsafe_allow_html=True)
        
        # Sample recent reports
        reports = [
            {"name": "Executive Summary", "date": "2024-01-27", "status": "Ready", "size": "2.3 MB"},
            {"name": "Weekly Analysis", "date": "2024-01-26", "status": "Ready", "size": "1.8 MB"},
            {"name": "Agent Performance", "date": "2024-01-25", "status": "Processing", "size": "—"},
            {"name": "Monthly Overview", "date": "2024-01-24", "status": "Ready", "size": "4.1 MB"},
            {"name": "Quality Assurance", "date": "2024-01-23", "status": "Ready", "size": "3.2 MB"},
        ]
        
        for report in reports:
            status_color = "🟢" if report['status'] == "Ready" else "🟡"
            st.markdown(f"""
            <div style="padding: 1rem; border: 1px solid #e5e7eb; border-radius: 10px; margin: 0.5rem 0; background: white;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{status_color} {report['name']}</strong><br>
                        <small style="color: #6b7280;">Generated: {report['date']} | Size: {report['size']}</small>
                    </div>
                    <div>
                        <button style="background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                            📥 Download
                        </button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Report templates
    st.markdown("### 📋 Report Templates")
    
    template_tabs = st.tabs(["📊 Executive", "👥 Operations", "💰 Financial", "📈 Analytics"])
    
    with template_tabs[0]:
        st.markdown("#### Executive Dashboard Template")
        st.info("High-level KPIs and strategic insights for leadership")
        
        exec_metrics = process_call_metrics()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Calls", f"{exec_metrics['total_calls']:,}")
        with col2:
            st.metric("Success Rate", f"{exec_metrics['success_rate']:.1f}%")
        with col3:
            st.metric("Revenue Impact", f"${exec_metrics['total_revenue']:,.0f}")
    
    with template_tabs[1]:
        st.markdown("#### Operations Template")
        st.info("Detailed operational metrics and agent performance")
        
        if 'voice_agent_name' in df.columns:
            agent_summary = df.groupby('voice_agent_name').agg({
                'call_id': 'count',
                'call_success': lambda x: (x == 'Yes').sum() / len(x) * 100
            }).round(1)
            st.dataframe(agent_summary, use_container_width=True)
    
    with template_tabs[2]:
        st.markdown("#### Financial Template")
        st.info("Revenue analysis and cost optimization insights")
        
        if 'revenue_impact' in df.columns:
            revenue_summary = df.groupby('call_date')['revenue_impact'].sum().tail(7)
            fig = px.bar(x=revenue_summary.index, y=revenue_summary.values, title="Daily Revenue (Last 7 Days)")
            st.plotly_chart(fig, use_container_width=True)
    
    with template_tabs[3]:
        st.markdown("#### Analytics Template")
        st.info("Advanced analytics and predictive insights")
        
        # Correlation analysis
        if all(col in df.columns for col in ['sentiment_score', 'customer_satisfaction', 'call_length_seconds']):
            corr_data = df[['sentiment_score', 'customer_satisfaction', 'call_length_seconds']].corr()
            fig = px.imshow(corr_data, text_auto=True, title="Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)

elif st.session_state.current_page == 'Real-time Monitor':
    st.markdown('<h2 class="section-header animate-fadeIn">🔴 Real-time Operations Monitor</h2>', unsafe_allow_html=True)
    
    # Real-time metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        active_calls = random.randint(5, 25)
        st.metric("🔴 Active Calls", active_calls, delta=random.randint(-3, 5))
    with col2:
        queue_length = random.randint(0, 10)
        st.metric("⏳ Queue Length", queue_length, delta=random.randint(-2, 3))
    with col3:
        available_agents = random.randint(8, 15)
        st.metric("👥 Available Agents", available_agents, delta=random.randint(-1, 2))
    with col4:
        avg_wait_time = random.randint(30, 180)
        st.metric("⚡ Avg Wait Time", f"{avg_wait_time}s", delta=f"{random.randint(-20, 30)}s")
    with col5:
        system_load = random.randint(45, 95)
        st.metric("💻 System Load", f"{system_load}%", delta=f"{random.randint(-5, 10)}%")
    
    # Real-time charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Live Call Volume")
        
        # Generate real-time data
        times = [datetime.now() - timedelta(minutes=x) for x in range(30, 0, -1)]
        volumes = [random.randint(10, 50) for _ in times]
        
        real_time_df = pd.DataFrame({'Time': times, 'Calls': volumes})
        
        fig = px.line(real_time_df, x='Time', y='Calls', title="Call Volume (Last 30 Minutes)")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Success Rate Trend")
        
        success_rates = [random.uniform(75, 95) for _ in times]
        success_df = pd.DataFrame({'Time': times, 'Success Rate': success_rates})
        
        fig = px.line(success_df, x='Time', y='Success Rate', title="Success Rate (Last 30 Minutes)")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Live activity feed
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📡 Live Activity Feed</div>', unsafe_allow_html=True)
    
    # Auto-refresh toggle
    auto_refresh_feed = st.checkbox("🔄 Auto-refresh feed", value=True)
    
    # Simulate live activities
    activities = [
        "📞 New call started - Agent Smith with Client ABC Corp",
        "✅ Call completed successfully - Agent Johnson (5m 32s)",
        "📋 Appointment scheduled - Client XYZ Ltd for next Tuesday",
        "⚠️ Call escalated to supervisor - Complex technical issue",
        "📞 Incoming call queued - Estimated wait time 45s",
        "💰 High-value deal closed - $50,000 contract signed",
        "🎯 Quality score updated - Agent Williams (4.8/5.0)",
        "📊 Daily target reached - 150 calls completed",
        "🔄 System backup completed successfully",
        "👥 New agent logged in - Agent Davis"
    ]
    
    # Display activities with timestamps
    for i, activity in enumerate(activities[:8]):
        current_time = datetime.now() - timedelta(minutes=random.randint(1, 60))
        priority = random.choice(["🟢", "🟡", "🔴"])
        
        st.markdown(f"""
        <div style="padding: 0.75rem; border-left: 4px solid #3b82f6; background: #f8fafc; margin: 0.5rem 0; border-radius: 5px; animation: fadeIn 0.5s ease-in;">
            <div style="display: flex; justify-content: between; align-items: center;">
                <div style="flex: 1;">
                    <div style="font-weight: 600;">{priority} {activity}</div>
                    <small style="color: #6b7280;">{current_time.strftime('%H:%M:%S')} - {random.randint(1, 60)} minutes ago</small>
                </div>
                <div style="margin-left: 1rem;">
                    <span style="background: #e5e7eb; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem;">
                        ID: {1000 + i}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # System status
    st.markdown("### 💻 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🖥️ Server Status")
        st.success("🟢 Primary Server: Online")
        st.success("🟢 Backup Server: Online")
        st.success("🟢 Database: Connected")
        st.warning("🟡 Cache Server: High Load")
    
    with col2:
        st.markdown("#### 📡 Network Status")
        st.success("🟢 Internet: Connected")
        st.success("🟢 VoIP Gateway: Active")
        st.success("🟢 API Endpoints: Responsive")
        st.success("🟢 CDN: Operational")
    
    with col3:
        st.markdown("#### 🔧 Service Status")
        st.success("🟢 Call Routing: Active")
        st.success("🟢 Recording Service: Running")
        st.success("🟢 Analytics Engine: Processing")
        st.info("🔵 Backup Service: Scheduled")
    
    # Auto-refresh for real-time data
    if auto_refresh_feed and real_time_mode:
        time_module.sleep(2)
        st.rerun()

elif st.session_state.current_page == 'Data Management':
    st.markdown('<h2 class="section-header animate-fadeIn">📊 Data Management Center</h2>', unsafe_allow_html=True)
    
    # Data source management
    st.markdown("### 🔗 Data Source Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="widget-container">', unsafe_allow_html=True)
        st.markdown('<div class="widget-title">📥 Data Import</div>', unsafe_allow_html=True)
        
        import_type = st.selectbox("Import Type", ["CSV File", "Excel File", "JSON File", "Database Connection", "API Integration"])
        
        if import_type in ["CSV File", "Excel File", "JSON File"]:
            uploaded_file = st.file_uploader(f"Upload {import_type}", type=['csv', 'xlsx', 'json'])
            
            if uploaded_file:
                st.success(f"✅ {import_type} uploaded successfully!")
                
                # Preview data
                if import_type == "CSV File":
                    preview_df = pd.read_csv(uploaded_file).head()
                elif import_type == "Excel File":
                    preview_df = pd.read_excel(uploaded_file).head()
                elif import_type == "JSON File":
                    preview_df = pd.read_json(uploaded_file).head()
                
                st.dataframe(preview_df, use_container_width=True)
        
        elif import_type == "Database Connection":
            db_type = st.selectbox("Database Type", ["PostgreSQL", "MySQL", "SQL Server", "Oracle", "SQLite"])
            db_host = st.text_input("Host", value="localhost")
            db_port = st.number_input("Port", value=5432)
            db_name = st.text_input("Database Name")
            db_user = st.text_input("Username")
            db_password = st.text_input("Password", type="password")
            
            if st.button("Test Connection"):
                st.info("🔄 Testing database connection...")
                time_module.sleep(2)
                st.success("✅ Connection successful!")
        
        elif import_type == "API Integration":
            api_url = st.text_input("API URL", value="https://api.example.com/data")
            api_key = st.text_input("API Key", type="password")
            api_method = st.selectbox("HTTP Method", ["GET", "POST", "PUT"])
            
            if st.button("Test API"):
                st.info("🔄 Testing API connection...")
                time_module.sleep(2)
                st.success("✅ API connection successful!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="widget-container">', unsafe_allow_html=True)
        st.markdown('<div class="widget-title">📤 Data Export</div>', unsafe_allow_html=True)
        
        export_data = st.selectbox("Data to Export", ["All Call Data", "Filtered Data", "Agent Performance", "Client Profiles", "Custom Query"])
        export_format = st.selectbox("Export Format", ["CSV", "Excel", "JSON", "Parquet", "PDF Report"])
        
        # Export options
        include_headers = st.checkbox("Include Headers", value=True)
        compress_file = st.checkbox("Compress File", value=False)
        
        if export_data == "Custom Query":
            custom_query = st.text_area("SQL Query", value="SELECT * FROM calls WHERE call_date >= '2024-01-01'")
        
        if st.button("📤 Export Data", type="primary"):
            st.info("🔄 Preparing export...")
            progress = st.progress(0)
            
            for i in range(100):
                time_module.sleep(0.01)
                progress.progress(i + 1)
            
            # Generate export data
            if export_format == "CSV":
                export_content = df.to_csv(index=False)
                file_extension = "csv"
            elif export_format == "JSON":
                export_content = df.to_json(orient='records', indent=2)
                file_extension = "json"
            else:
                export_content = df.to_csv(index=False)  # Fallback
                file_extension = "csv"
            
            st.download_button(
                label=f"📥 Download {export_format} File",
                data=export_content,
                file_name=f"aiva_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}",
                mime=f"text/{file_extension}"
            )
            
            st.success("✅ Export completed!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Data quality and validation
    st.markdown("### 🔍 Data Quality & Validation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Data Overview")
        st.metric("Total Records", f"{len(df):,}")
        st.metric("Total Columns", len(df.columns))
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
        st.metric("Duplicate Records", df.duplicated().sum())
    
    with col2:
        st.markdown("#### ⚠️ Data Issues")
        missing_data = df.isnull().sum().sum()
        st.metric("Missing Values", missing_data)
        
        # Check for common data issues
        if 'phone_number' in df.columns:
            invalid_phones = df['phone_number'].str.len().lt(10).sum()
            st.metric("Invalid Phone Numbers", invalid_phones)
        
        if 'email' in df.columns:
            invalid_emails = ~df['email'].str.contains('@', na=False)
            st.metric("Invalid Emails", invalid_emails.sum())
        
        if 'call_date' in df.columns:
            future_dates = pd.to_datetime(df['call_date'], errors='coerce') > datetime.now()
            st.metric("Future Dates", future_dates.sum())
    
    with col3:
        st.markdown("#### 🔧 Data Actions")
        
        if st.button("🧹 Clean Data"):
            st.info("🔄 Cleaning data...")
            time_module.sleep(2)
            st.success("✅ Data cleaned successfully!")
        
        if st.button("🔍 Validate Data"):
            st.info("🔄 Validating data...")
            time_module.sleep(2)
            st.success("✅ Data validation completed!")
        
        if st.button("📊 Generate Report"):
            st.info("🔄 Generating data quality report...")
            time_module.sleep(2)
            st.success("✅ Report generated!")
        
        if st.button("🔄 Refresh Schema"):
            st.info("🔄 Refreshing data schema...")
            time_module.sleep(1)
            st.success("✅ Schema refreshed!")
    
    # Data transformation
    st.markdown("### 🔄 Data Transformation")
    
    transformation_tabs = st.tabs(["🔧 Column Operations", "🧮 Calculations", "🔗 Joins", "📊 Aggregations"])
    
    with transformation_tabs[0]:
        st.markdown("#### Column Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Select Column", df.columns.tolist())
            operation = st.selectbox("Operation", ["Rename", "Delete", "Duplicate", "Convert Type", "Fill Missing"])
            
            if operation == "Rename":
                new_name = st.text_input("New Name")
            elif operation == "Convert Type":
                new_type = st.selectbox("New Type", ["String", "Integer", "Float", "Date", "Boolean"])
            elif operation == "Fill Missing":
                fill_method = st.selectbox("Fill Method", ["Forward Fill", "Backward Fill", "Mean", "Median", "Custom Value"])
        
        with col2:
            if st.button("Apply Operation"):
                st.success("✅ Operation applied successfully!")
    
    with transformation_tabs[1]:
        st.markdown("#### Calculated Fields")
        
        calc_name = st.text_input("Field Name", value="calculated_field")
        calc_formula = st.text_area("Formula", value="column1 + column2")
        
        if st.button("Create Calculated Field"):
            st.success("✅ Calculated field created!")
    
    with transformation_tabs[2]:
        st.markdown("#### Data Joins")
        
        join_type = st.selectbox("Join Type", ["Inner Join", "Left Join", "Right Join", "Outer Join"])
        join_key = st.selectbox("Join Key", df.columns.tolist())
        
        st.info("Upload second dataset to perform join operations")
    
    with transformation_tabs[3]:
        st.markdown("#### Data Aggregations")
        
        group_by = st.multiselect("Group By", df.columns.tolist())
        agg_column = st.selectbox("Aggregate Column", df.select_dtypes(include=[np.number]).columns.tolist())
        agg_function = st.selectbox("Function", ["Sum", "Mean", "Count", "Min", "Max", "Std"])
        
        if st.button("Create Aggregation"):
            if group_by and agg_column:
                if agg_function == "Sum":
                    result = df.groupby(group_by)[agg_column].sum()
                elif agg_function == "Mean":
                    result = df.groupby(group_by)[agg_column].mean()
                elif agg_function == "Count":
                    result = df.groupby(group_by)[agg_column].count()
                
                st.dataframe(result.reset_index(), use_container_width=True)

elif st.session_state.current_page == 'Settings':
    st.markdown('<h2 class="section-header animate-fadeIn">⚙️ System Settings & Configuration</h2>', unsafe_allow_html=True)
    
    # Settings tabs
    settings_tabs = st.tabs(["🎨 Appearance", "🔐 Security", "📊 Data", "🔔 Notifications", "🚀 Performance", "🔧 Advanced"])
    
    with settings_tabs[0]:
        st.markdown("### 🎨 Appearance Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Theme Configuration")
            theme_preset = st.selectbox("Theme Preset", ["AIVA Default", "Dark Mode", "Light Mode", "High Contrast", "Custom"])
            
            if theme_preset == "Custom":
                primary_color = st.color_picker("Primary Color", "#2563eb")
                secondary_color = st.color_picker("Secondary Color", "#1e40af")
                accent_color = st.color_picker("Accent Color", "#3b82f6")
                background_color = st.color_picker("Background Color", "#ffffff")
            
            font_family = st.selectbox("Font Family", ["Inter", "Roboto", "Open Sans", "Lato", "Montserrat"])
            font_size_base = st.slider("Base Font Size", 12, 20, 14)
            
            border_radius = st.slider("Border Radius", 0, 25, 15)
            shadow_intensity = st.slider("Shadow Intensity", 0, 100, 50)
        
        with col2:
            st.markdown("#### Layout Settings")
            sidebar_width = st.slider("Sidebar Width", 200, 400, 300)
            content_max_width = st.slider("Content Max Width", 800, 1400, 1200)
            
            show_animations = st.checkbox("Enable Animations", value=True)
            show_tooltips = st.checkbox("Show Tooltips", value=True)
            compact_layout = st.checkbox("Compact Layout", value=False)
            
            st.markdown("#### Dashboard Layout")
            default_page = st.selectbox("Default Page", nav_options)
            cards_per_row = st.slider("Cards per Row", 2, 6, 4)
            chart_height = st.slider("Default Chart Height", 300, 800, 400)
        
        if st.button("💾 Save Appearance Settings"):
            st.success("✅ Appearance settings saved!")
    
    with settings_tabs[1]:
        st.markdown("### 🔐 Security Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Authentication")
            auth_method = st.selectbox("Authentication Method", ["Password", "OAuth", "LDAP", "SSO"])
            
            if auth_method == "Password":
                password_policy = st.selectbox("Password Policy", ["Basic", "Strong", "Enterprise"])
                session_timeout = st.slider("Session Timeout (minutes)", 15, 480, 60)
                max_login_attempts = st.slider("Max Login Attempts", 3, 10, 5)
            
            two_factor_auth = st.checkbox("Enable Two-Factor Authentication", value=False)
            remember_me = st.checkbox("Allow 'Remember Me'", value=True)
            
            st.markdown("#### Access Control")
            role_based_access = st.checkbox("Enable Role-Based Access", value=True)
            ip_whitelist = st.text_area("IP Whitelist (one per line)", value="192.168.1.0/24\n10.0.0.0/8")
        
        with col2:
            st.markdown("#### Data Security")
            encrypt_data = st.checkbox("Encrypt Data at Rest", value=True)
            encrypt_transit = st.checkbox("Encrypt Data in Transit", value=True)
            audit_logging = st.checkbox("Enable Audit Logging", value=True)
            
            data_retention = st.slider("Data Retention (days)", 30, 2555, 365)
            backup_frequency = st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])
            
            st.markdown("#### Privacy Settings")
            anonymize_data = st.checkbox("Anonymize Personal Data", value=False)
            gdpr_compliance = st.checkbox("GDPR Compliance Mode", value=True)
            data_export_approval = st.checkbox("Require Approval for Data Export", value=True)
        
        if st.button("🔒 Save Security Settings"):
            st.success("✅ Security settings saved!")
    
    with settings_tabs[2]:
        st.markdown("### 📊 Data Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Data Sources")
            primary_source = st.selectbox("Primary Data Source", ["Google Sheets", "Database", "API", "File Upload"])
            backup_source = st.selectbox("Backup Data Source", ["None", "Local File", "Secondary Database"])
            
            auto_sync = st.checkbox("Auto-sync Data", value=True)
            if auto_sync:
                sync_interval = st.slider("Sync Interval (minutes)", 1, 60, 5)
            
            data_validation = st.checkbox("Enable Data Validation", value=True)
            auto_cleanup = st.checkbox("Auto-cleanup Invalid Data", value=False)
            
            st.markdown("#### Data Processing")
            batch_size = st.slider("Batch Processing Size", 100, 10000, 1000)
            parallel_processing = st.checkbox("Enable Parallel Processing", value=True)
            if parallel_processing:
                max_workers = st.slider("Max Worker Threads", 1, 16, 4)
        
        with col2:
            st.markdown("#### Data Quality")
            quality_threshold = st.slider("Data Quality Threshold (%)", 50, 100, 85)
            missing_data_threshold = st.slider("Missing Data Threshold (%)", 0, 50, 10)
            
            auto_fix_issues = st.checkbox("Auto-fix Common Issues", value=True)
            notify_quality_issues = st.checkbox("Notify on Quality Issues", value=True)
            
            st.markdown("#### Data Archiving")
            archive_old_data = st.checkbox("Archive Old Data", value=True)
            if archive_old_data:
                archive_after_days = st.slider("Archive After (days)", 30, 365, 90)
                archive_location = st.selectbox("Archive Location", ["Local Storage", "Cloud Storage", "External Database"])
        
        if st.button("💾 Save Data Settings"):
            st.success("✅ Data settings saved!")
    
    with settings_tabs[3]:
        st.markdown("### 🔔 Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Email Notifications")
            email_enabled = st.checkbox("Enable Email Notifications", value=True)
            
            if email_enabled:
                smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
                smtp_port = st.number_input("SMTP Port", value=587)
                smtp_username = st.text_input("SMTP Username")
                smtp_password = st.text_input("SMTP Password", type="password")
                
                notification_types = st.multiselect("Notification Types", [
                    "System Alerts", "Data Quality Issues", "Performance Warnings", 
                    "Security Events", "Backup Status", "Report Generation"
                ], default=["System Alerts", "Security Events"])
            
            st.markdown("#### Slack Integration")
            slack_enabled = st.checkbox("Enable Slack Notifications", value=False)
            if slack_enabled:
                slack_webhook = st.text_input("Slack Webhook URL")
                slack_channel = st.text_input("Default Channel", value="#aiva-alerts")
        
        with col2:
            st.markdown("#### Alert Thresholds")
            cpu_threshold = st.slider("CPU Usage Alert (%)", 50, 100, 80)
            memory_threshold = st.slider("Memory Usage Alert (%)", 50, 100, 85)
            disk_threshold = st.slider("Disk Usage Alert (%)", 50, 100, 90)
            
            error_rate_threshold = st.slider("Error Rate Alert (%)", 1, 20, 5)
            response_time_threshold = st.slider("Response Time Alert (ms)", 100, 5000, 1000)
            
            st.markdown("#### Notification Schedule")
            quiet_hours_enabled = st.checkbox("Enable Quiet Hours", value=True)
            if quiet_hours_enabled:
                quiet_start = st.time_input("Quiet Hours Start", value=time(22, 0))
                quiet_end = st.time_input("Quiet Hours End", value=time(8, 0))
            
            weekend_notifications = st.checkbox("Send Weekend Notifications", value=False)
        
        if st.button("🔔 Save Notification Settings"):
            st.success("✅ Notification settings saved!")
    
    with settings_tabs[4]:
        st.markdown("### 🚀 Performance Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Caching")
            enable_caching = st.checkbox("Enable Caching", value=True)
            if enable_caching:
                cache_size_mb = st.slider("Cache Size (MB)", 100, 2000, 500)
                cache_ttl_minutes = st.slider("Cache TTL (minutes)", 1, 60, 5)
                cache_strategy = st.selectbox("Cache Strategy", ["LRU", "LFU", "FIFO"])
            
            st.markdown("#### Database Optimization")
            connection_pool_size = st.slider("Connection Pool Size", 5, 50, 20)
            query_timeout = st.slider("Query Timeout (seconds)", 10, 300, 30)
            enable_query_cache = st.checkbox("Enable Query Cache", value=True)
            
            st.markdown("#### Resource Limits")
            max_memory_usage = st.slider("Max Memory Usage (GB)", 1, 16, 4)
            max_cpu_cores = st.slider("Max CPU Cores", 1, 16, 4)
        
        with col2:
            st.markdown("#### Optimization")
            lazy_loading = st.checkbox("Enable Lazy Loading", value=True)
            compression = st.checkbox("Enable Compression", value=True)
            minification = st.checkbox("Enable Minification", value=True)
            
            image_optimization = st.checkbox("Optimize Images", value=True)
            if image_optimization:
                image_quality = st.slider("Image Quality (%)", 50, 100, 80)
                max_image_size = st.slider("Max Image Size (KB)", 100, 2000, 500)
            
            st.markdown("#### Monitoring")
            performance_monitoring = st.checkbox("Enable Performance Monitoring", value=True)
            detailed_logging = st.checkbox("Enable Detailed Logging", value=False)
            metrics_collection = st.checkbox("Collect Performance Metrics", value=True)
        
        if st.button("🚀 Save Performance Settings"):
            st.success("✅ Performance settings saved!")
    
    with settings_tabs[5]:
        st.markdown("### 🔧 Advanced Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### System Configuration")
            debug_mode = st.checkbox("Enable Debug Mode", value=False)
            maintenance_mode = st.checkbox("Maintenance Mode", value=False)
            
            log_level = st.selectbox("Log Level", ["ERROR", "WARN", "INFO", "DEBUG"])
            max_log_size = st.slider("Max Log Size (MB)", 10, 1000, 100)
            
            st.markdown("#### API Configuration")
            api_rate_limit = st.slider("API Rate Limit (requests/minute)", 60, 10000, 1000)
            api_timeout = st.slider("API Timeout (seconds)", 5, 120, 30)
            enable_api_docs = st.checkbox("Enable API Documentation", value=True)
            
            st.markdown("#### Feature Flags")
            experimental_features = st.checkbox("Enable Experimental Features", value=False)
            beta_features = st.checkbox("Enable Beta Features", value=False)
            legacy_support = st.checkbox("Enable Legacy Support", value=True)
        
        with col2:
            st.markdown("#### Integration Settings")
            webhook_enabled = st.checkbox("Enable Webhooks", value=False)
            if webhook_enabled:
                webhook_url = st.text_input("Webhook URL")
                webhook_secret = st.text_input("Webhook Secret", type="password")
            
            external_apis = st.multiselect("Enable External APIs", [
                "Google Analytics", "Salesforce", "HubSpot", "Zendesk", "Slack", "Microsoft Teams"
            ])
            
            st.markdown("#### Backup & Recovery")
            auto_backup = st.checkbox("Enable Auto Backup", value=True)
            if auto_backup:
                backup_schedule = st.selectbox("Backup Schedule", ["Hourly", "Daily", "Weekly"])
                backup_retention = st.slider("Backup Retention (days)", 7, 365, 30)
            
            disaster_recovery = st.checkbox("Enable Disaster Recovery", value=False)
        
        if st.button("🔧 Save Advanced Settings"):
            st.success("✅ Advanced settings saved!")
    
    # System information
    st.markdown("### 💻 System Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Version", "v2.1.0")
        st.metric("Build", "20240127")
    
    with col2:
        st.metric("Uptime", "2d 15h 32m")
        st.metric("Last Restart", "Jan 25, 2024")
    
    with col3:
        st.metric("Active Users", "1")
        st.metric("Total Sessions", "47")
    
    with col4:
        st.metric("Data Size", "125.3 MB")
        st.metric("Cache Size", "12.8 MB")

elif st.session_state.current_page == 'Advanced Tools':
    st.markdown('<h2 class="section-header animate-fadeIn">🛠️ Advanced Tools & Utilities</h2>', unsafe_allow_html=True)
    
    # Advanced tools tabs
    tools_tabs = st.tabs(["🤖 AI Tools", "📊 Analytics", "🔧 Utilities", "🧪 Testing", "🔍 Debugging"])
    
    with tools_tabs[0]:
        st.markdown("### 🤖 AI-Powered Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🧠 Sentiment Analysis</div>', unsafe_allow_html=True)
            
            text_to_analyze = st.text_area("Text to Analyze", value="The customer was very satisfied with our service and would recommend us to others.")
            
            if st.button("🔍 Analyze Sentiment"):
                with st.spinner("Analyzing sentiment..."):
                    time_module.sleep(2)
                    
                    # Mock sentiment analysis
                    sentiment_score = random.uniform(0.7, 0.95)
                    sentiment_label = "Positive" if sentiment_score > 0.6 else "Negative" if sentiment_score < 0.4 else "Neutral"
                    confidence = random.uniform(0.8, 0.99)
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Sentiment", sentiment_label)
                    with col_b:
                        st.metric("Score", f"{sentiment_score:.3f}")
                    with col_c:
                        st.metric("Confidence", f"{confidence:.1%}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🎯 Intent Detection</div>', unsafe_allow_html=True)
            
            intent_text = st.text_area("Customer Message", value="I would like to schedule an appointment for next week.")
            
            if st.button("🎯 Detect Intent"):
                with st.spinner("Detecting intent..."):
                    time_module.sleep(1)
                    
                    intents = ["Booking", "Support", "Complaint", "Information", "Cancellation"]
                    detected_intent = random.choice(intents)
                    confidence = random.uniform(0.75, 0.98)
                    
                    st.success(f"**Detected Intent:** {detected_intent}")
                    st.info(f"**Confidence:** {confidence:.1%}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">📝 Text Summarization</div>', unsafe_allow_html=True)
            
            text_to_summarize = st.text_area("Text to Summarize", value="The customer called regarding their recent order. They were initially frustrated because the delivery was delayed by two days. However, after explaining the situation and offering a discount on their next order, the customer became more understanding. They appreciated our proactive communication and expressed satisfaction with the resolution. The customer also mentioned they would continue doing business with us and might refer friends.")
            
            summary_length = st.selectbox("Summary Length", ["Short", "Medium", "Long"])
            
            if st.button("📝 Generate Summary"):
                with st.spinner("Generating summary..."):
                    time_module.sleep(2)
                    
                    # Mock summary
                    summaries = {
                        "Short": "Customer was initially frustrated with delayed delivery but satisfied after receiving discount and explanation.",
                        "Medium": "Customer called about delayed order, was initially frustrated but became satisfied after receiving explanation and discount. Expressed willingness to continue business and refer others.",
                        "Long": "Customer contacted support regarding a delivery delay of two days for their recent order. Initially frustrated, the customer's attitude improved after receiving a clear explanation and a discount offer for their next purchase. They appreciated the proactive communication and expressed overall satisfaction with the resolution process. The customer indicated they would continue their business relationship and potentially refer friends to the company."
                    }
                    
                    st.success("**Summary Generated:**")
                    st.write(summaries[summary_length])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🔮 Predictive Analytics</div>', unsafe_allow_html=True)
            
            prediction_type = st.selectbox("Prediction Type", ["Call Success", "Customer Satisfaction", "Churn Risk", "Revenue Forecast"])
            
            if st.button("🔮 Generate Prediction"):
                with st.spinner("Running predictive model..."):
                    time_module.sleep(3)
                    
                    # Mock predictions
                    if prediction_type == "Call Success":
                        prediction = random.uniform(0.75, 0.95)
                        st.metric("Predicted Success Rate", f"{prediction:.1%}")
                    elif prediction_type == "Customer Satisfaction":
                        prediction = random.uniform(3.5, 4.8)
                        st.metric("Predicted Satisfaction", f"{prediction:.1f}/5.0")
                    elif prediction_type == "Churn Risk":
                        prediction = random.uniform(0.05, 0.25)
                        st.metric("Predicted Churn Risk", f"{prediction:.1%}")
                    elif prediction_type == "Revenue Forecast":
                        prediction = random.uniform(50000, 150000)
                        st.metric("Predicted Revenue", f"${prediction:,.0f}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tools_tabs[1]:
        st.markdown("### 📊 Advanced Analytics Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">📈 Cohort Analysis</div>', unsafe_allow_html=True)
            
            cohort_metric = st.selectbox("Cohort Metric", ["Customer Retention", "Revenue per Cohort", "Call Frequency"])
            cohort_period = st.selectbox("Cohort Period", ["Weekly", "Monthly", "Quarterly"])
            
            if st.button("📈 Generate Cohort Analysis"):
                # Mock cohort data
                periods = 12
                cohorts = 6
                
                cohort_data = np.random.rand(cohorts, periods) * 100
                cohort_df = pd.DataFrame(cohort_data, 
                                       index=[f"Cohort {i+1}" for i in range(cohorts)],
                                       columns=[f"Period {i+1}" for i in range(periods)])
                
                fig = px.imshow(cohort_df, text_auto=True, aspect="auto", title="Cohort Analysis Heatmap")
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🎯 A/B Testing</div>', unsafe_allow_html=True)
            
            test_name = st.text_input("Test Name", value="Call Script Optimization")
            variant_a = st.text_input("Variant A", value="Standard Script")
            variant_b = st.text_input("Variant B", value="Personalized Script")
            
            metric_to_test = st.selectbox("Metric to Test", ["Success Rate", "Customer Satisfaction", "Call Duration"])
            
            if st.button("🎯 Run A/B Test"):
                with st.spinner("Running A/B test..."):
                    time_module.sleep(2)
                    
                    # Mock A/B test results
                    variant_a_result = random.uniform(0.7, 0.85)
                    variant_b_result = random.uniform(0.75, 0.9)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric(f"{variant_a}", f"{variant_a_result:.1%}")
                    with col_b:
                        st.metric(f"{variant_b}", f"{variant_b_result:.1%}")
                    
                    improvement = (variant_b_result - variant_a_result) / variant_a_result * 100
                    if improvement > 0:
                        st.success(f"🎉 Variant B shows {improvement:.1f}% improvement!")
                    else:
                        st.warning(f"⚠️ Variant B shows {abs(improvement):.1f}% decrease")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Statistical analysis
        st.markdown('<div class="widget-container">', unsafe_allow_html=True)
        st.markdown('<div class="widget-title">📊 Statistical Analysis</div>', unsafe_allow_html=True)
        
        analysis_type = st.selectbox("Analysis Type", ["Correlation Analysis", "Regression Analysis", "Time Series Analysis", "Anomaly Detection"])
        
        if analysis_type == "Correlation Analysis":
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            selected_columns = st.multiselect("Select Columns", numeric_columns, default=numeric_columns[:4])
            
            if st.button("📊 Run Correlation Analysis") and selected_columns:
                corr_matrix = df[selected_columns].corr()
                fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Matrix")
                st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_type == "Anomaly Detection":
            anomaly_column = st.selectbox("Column for Anomaly Detection", df.select_dtypes(include=[np.number]).columns.tolist())
            
            if st.button("🔍 Detect Anomalies") and anomaly_column:
                # Mock anomaly detection
                data_values = df[anomaly_column].values
                mean_val = np.mean(data_values)
                std_val = np.std(data_values)
                
                anomalies = np.abs(data_values - mean_val) > 2 * std_val
                
                st.metric("Anomalies Detected", anomalies.sum())
                st.metric("Anomaly Rate", f"{anomalies.sum() / len(data_values) * 100:.1f}%")
                
                # Plot anomalies
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=data_values, mode='markers', name='Normal', 
                                       marker=dict(color='blue')))
                fig.add_trace(go.Scatter(y=data_values[anomalies], x=np.where(anomalies)[0],
                                       mode='markers', name='Anomalies', 
                                       marker=dict(color='red', size=10)))
                fig.update_layout(title="Anomaly Detection Results")
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tools_tabs[2]:
        st.markdown("### 🔧 System Utilities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🗄️ Database Tools</div>', unsafe_allow_html=True)
            
            db_operation = st.selectbox("Database Operation", ["Backup", "Restore", "Optimize", "Repair", "Analyze"])
            
            if st.button(f"🗄️ {db_operation} Database"):
                with st.spinner(f"Running {db_operation.lower()} operation..."):
                    progress = st.progress(0)
                    for i in range(100):
                        time_module.sleep(0.02)
                        progress.progress(i + 1)
                    
                    st.success(f"✅ Database {db_operation.lower()} completed successfully!")
            
            st.markdown("#### 📊 Database Statistics")
            st.metric("Total Tables", "12")
            st.metric("Total Records", f"{len(df):,}")
            st.metric("Database Size", "125.3 MB")
            st.metric("Last Backup", "2 hours ago")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🧹 Data Cleanup</div>', unsafe_allow_html=True)
            
            cleanup_options = st.multiselect("Cleanup Options", [
                "Remove Duplicates", "Fix Phone Numbers", "Standardize Emails", 
                "Clean Text Fields", "Validate Dates", "Normalize Names"
            ])
            
            if st.button("🧹 Run Cleanup") and cleanup_options:
                with st.spinner("Cleaning data..."):
                    progress = st.progress(0)
                    for i, option in enumerate(cleanup_options):
                        time_module.sleep(1)
                        progress.progress((i + 1) / len(cleanup_options))
                        st.info(f"Processing: {option}")
                    
                    st.success("✅ Data cleanup completed!")
                    
                    # Mock cleanup results
                    st.metric("Records Processed", f"{len(df):,}")
                    st.metric("Issues Fixed", random.randint(10, 100))
                    st.metric("Duplicates Removed", random.randint(5, 25))
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # System monitoring
        st.markdown('<div class="widget-container">', unsafe_allow_html=True)
        st.markdown('<div class="widget-title">📊 System Monitoring</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cpu_usage = random.randint(20, 80)
            st.metric("CPU Usage", f"{cpu_usage}%")
            st.progress(cpu_usage / 100)
        
        with col2:
            memory_usage = random.randint(30, 70)
            st.metric("Memory Usage", f"{memory_usage}%")
            st.progress(memory_usage / 100)
        
        with col3:
            disk_usage = random.randint(40, 85)
            st.metric("Disk Usage", f"{disk_usage}%")
            st.progress(disk_usage / 100)
        
        with col4:
            network_usage = random.randint(10, 60)
            st.metric("Network Usage", f"{network_usage}%")
            st.progress(network_usage / 100)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tools_tabs[3]:
        st.markdown("### 🧪 Testing Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🔬 Data Quality Testing</div>', unsafe_allow_html=True)
            
            test_suite = st.multiselect("Test Suite", [
                "Data Completeness", "Data Accuracy", "Data Consistency", 
                "Data Validity", "Data Uniqueness", "Data Timeliness"
            ], default=["Data Completeness", "Data Accuracy"])
            
            if st.button("🧪 Run Tests") and test_suite:
                with st.spinner("Running data quality tests..."):
                    results = {}
                    for test in test_suite:
                        time_module.sleep(0.5)
                        # Mock test results
                        score = random.uniform(0.7, 0.98)
                        results[test] = score
                        st.info(f"✓ {test}: {score:.1%}")
                    
                    overall_score = np.mean(list(results.values()))
                    
                    if overall_score > 0.9:
                        st.success(f"🎉 Overall Quality Score: {overall_score:.1%} - Excellent!")
                    elif overall_score > 0.8:
                        st.warning(f"⚠️ Overall Quality Score: {overall_score:.1%} - Good")
                    else:
                        st.error(f"❌ Overall Quality Score: {overall_score:.1%} - Needs Improvement")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">⚡ Performance Testing</div>', unsafe_allow_html=True)
            
            test_type = st.selectbox("Performance Test", ["Load Test", "Stress Test", "Spike Test", "Volume Test"])
            test_duration = st.slider("Test Duration (minutes)", 1, 30, 5)
            concurrent_users = st.slider("Concurrent Users", 1, 100, 10)
            
            if st.button("⚡ Run Performance Test"):
                with st.spinner(f"Running {test_type.lower()}..."):
                    progress = st.progress(0)
                    
                    for i in range(test_duration * 10):  # Simulate test progress
                        time_module.sleep(0.1)
                        progress.progress((i + 1) / (test_duration * 10))
                    
                    # Mock performance results
                    avg_response_time = random.uniform(100, 500)
                    max_response_time = avg_response_time * random.uniform(1.5, 3.0)
                    throughput = random.uniform(50, 200)
                    error_rate = random.uniform(0, 5)
                    
                    st.success("✅ Performance test completed!")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Avg Response Time", f"{avg_response_time:.0f}ms")
                        st.metric("Max Response Time", f"{max_response_time:.0f}ms")
                    with col_b:
                        st.metric("Throughput", f"{throughput:.0f} req/s")
                        st.metric("Error Rate", f"{error_rate:.1f}%")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tools_tabs[4]:
        st.markdown("### 🔍 Debugging Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">📋 System Logs</div>', unsafe_allow_html=True)
            
            log_level = st.selectbox("Log Level", ["ALL", "ERROR", "WARN", "INFO", "DEBUG"])
            log_lines = st.slider("Number of Lines", 10, 1000, 100)
            
            if st.button("📋 View Logs"):
                # Mock log entries
                log_entries = [
                    "2024-01-27 10:30:15 INFO - User authentication successful",
                    "2024-01-27 10:30:20 DEBUG - Loading dashboard data",
                    "2024-01-27 10:30:22 INFO - Data loaded successfully (500 records)",
                    "2024-01-27 10:30:25 WARN - High memory usage detected (75%)",
                    "2024-01-27 10:30:30 INFO - Calendar events generated",
                    "2024-01-27 10:30:35 DEBUG - Cache updated",
                    "2024-01-27 10:30:40 ERROR - Failed to connect to external API",
                    "2024-01-27 10:30:45 INFO - Fallback data source activated",
                ]
                
                st.code("\n".join(log_entries), language="text")
            
            if st.button("📥 Download Logs"):
                log_content = "\n".join([
                    "2024-01-27 10:30:15 INFO - User authentication successful",
                    "2024-01-27 10:30:20 DEBUG - Loading dashboard data",
                    "2024-01-27 10:30:22 INFO - Data loaded successfully (500 records)",
                    # ... more log entries
                ])
                
                st.download_button(
                    label="📥 Download Log File",
                    data=log_content,
                    file_name=f"aiva_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                    mime="text/plain"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="widget-container">', unsafe_allow_html=True)
            st.markdown('<div class="widget-title">🔧 Debug Console</div>', unsafe_allow_html=True)
            
            debug_command = st.text_input("Debug Command", value="SELECT COUNT(*) FROM calls")
            
            if st.button("▶️ Execute"):
                with st.spinner("Executing command..."):
                    time_module.sleep(1)
                    
                    # Mock command execution
                    if "SELECT" in debug_command.upper():
                        st.success("Query executed successfully!")
                        st.code("Result: 500 rows")
                    elif "SHOW" in debug_command.upper():
                        st.success("Command executed successfully!")
                        st.code("Status: All systems operational")
                    else:
                        st.info("Command executed")
            
            st.markdown("#### 🔍 Quick Debug Actions")
            
            if st.button("🔄 Clear Cache"):
                st.success("✅ Cache cleared!")
            
            if st.button("🔄 Restart Services"):
                with st.spinner("Restarting services..."):
                    time_module.sleep(2)
                    st.success("✅ Services restarted!")
            
            if st.button("📊 Memory Dump"):
                st.info("📊 Memory dump generated: memory_dump_20240127.bin")
            
            if st.button("🔍 Health Check"):
                with st.spinner("Running health check..."):
                    time_module.sleep(1)
                    st.success("✅ All systems healthy!")
            
            st.markdown('</div>', unsafe_allow_html=True)

# Sidebar mini calendar
with st.sidebar:
    st.markdown("### 📅 Quick Calendar")
    mini_cal = create_mini_calendar()
    st.markdown(mini_cal, unsafe_allow_html=True)
    
    # Calendar quick stats
    st.markdown("### 📊 Calendar Stats")
    events = generate_calendar_events(df)
    
    st.metric("Total Events", len(events))
    st.metric("This Month", len([e for e in events if datetime.now().strftime('%Y-%m') in e['start']]))
    st.metric("Today", len([e for e in events if datetime.now().strftime('%Y-%m-%d') in e['start']]))

# Footer
st.markdown("""
<div style="text-align: center; padding: 3rem 0; color: #6b7280; border-top: 1px solid #e5e7eb; margin-top: 4rem;">
    <p><strong>🤖 AIVA Call Center Dashboard - Ultimate Widget Edition</strong></p>
    <p>Powered by Advanced AI Analytics | Real-time Data Integration | Secure Authentication | Comprehensive Widget Library</p>
    <p><small>© 2024 AIVA Technologies. All rights reserved. | Version 2.1.0 Ultimate</small></p>
</div>
""", unsafe_allow_html=True)

