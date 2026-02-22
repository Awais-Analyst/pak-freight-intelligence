import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Pakistan Freight Intelligence",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

body {
    font-family: 'Montserrat', sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #e6e6e6;
}

.stApp {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

/* Header styling */
.main-header {
    background: linear-gradient(90deg, #0f3460 0%, #16537e 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.main-header h1 {
    color: #00ff88;
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

.main-header p {
    color: #b8c5d6;
    font-size: 1.1rem;
    margin-top: 0.5rem;
}

/* Card styling */
.metric-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.metric-card:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: translateY(-2px);
}

/* Input styling */
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    color: white !important;
}

.stNumberInput > div > div {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(90deg, #00ff88 0%, #00cc6a 100%) !important;
    color: #0a1929 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(0, 255, 136, 0.4) !important;
}

/* Table styling */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Expander styling */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.streamlit-expanderContent {
    background: rgba(255, 255, 255, 0.02) !important;
    border-radius: 0 0 8px 8px !important;
}

/* Green badge */
.green-badge {
    background: linear-gradient(90deg, #00ff88 0%, #00cc6a 100%);
    color: #0a1929;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    margin-left: 0.5rem;
}

/* Loading spinner */
.stSpinner > div {
    border-color: #00ff88 !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"  # Default for local development

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar navigation
st.sidebar.title("🚛 Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["🏠 Home", "📊 Live Rates", "🔮 Rate Predictor", "🗺️ Route Optimizer", "🤖 AI Agent", "📈 Analytics"]
)

# Sidebar settings
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Settings")
api_url = st.sidebar.text_input("API URL:", st.session_state.api_url)
st.session_state.api_url = api_url

# Main header
st.markdown("""
<div class="main-header">
    <h1>🚛 Pakistan Freight Intelligence</h1>
    <p>Pakistan's first real-time freight rate intelligence & route optimization platform</p>
</div>
""", unsafe_allow_html=True)

# Page routing
if page == "🏠 Home":
    from pages.home import show_home
    show_home(st.session_state.api_url)

elif page == "📊 Live Rates":
    from pages.live_rates import show_live_rates
    show_live_rates(st.session_state.api_url)

elif page == "🔮 Rate Predictor":
    from pages.predictor import show_predictor
    show_predictor(st.session_state.api_url)

elif page == "🗺️ Route Optimizer":
    from pages.optimizer import show_optimizer
    show_optimizer(st.session_state.api_url)

elif page == "🤖 AI Agent":
    from pages.ai_agent import show_ai_agent
    show_ai_agent(st.session_state.api_url)

elif page == "📈 Analytics":
    from pages.analytics import show_analytics
    show_analytics(st.session_state.api_url)

# Footer
st.markdown("""
<div class="footer">
    <p>Made with ❤️ for Pakistan's trucking community | Data aggregated from public sources | 
    <a href="https://github.com/yourusername/pak-freight-intelligence" style="color: #00ff88;">GitHub</a></p>
</div>
""", unsafe_allow_html=True)