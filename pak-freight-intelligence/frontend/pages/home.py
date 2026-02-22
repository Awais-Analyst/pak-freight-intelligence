import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def show_home(api_url):
    """Display the home page with live overview"""
    
    # Welcome section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
            <h2 style="color: #00ff88; margin-bottom: 1rem;">Welcome to Pakistan's First Freight Intelligence Platform</h2>
            <p style="font-size: 1.1rem; line-height: 1.6;">
                Get real-time freight rates, AI-powered predictions, and optimal route planning for Pakistan's 
                road freight industry. Built for truckers, by truckers.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Quick stats
        try:
            health_response = requests.get(f"{api_url}/health", timeout=5)
            if health_response.status_code == 200:
                health = health_response.json()
                st.success("✅ API Connected")
                st.json(health.get('services', {}))
            else:
                st.error("❌ API Disconnected")
        except:
            st.error("❌ API Disconnected")
    
    # Key Features
    st.markdown("<h2 style='color: #00ff88; margin-top: 3rem;'>🚀 Key Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        {
            "icon": "📊",
            "title": "Live Rates",
            "desc": "Real-time median freight rates from marketplace data"
        },
        {
            "icon": "🔮",
            "title": "AI Predictions",
            "desc": "ML-powered rate forecasts for tomorrow and next week"
        },
        {
            "icon": "🗺️",
            "title": "Route Optimization",
            "desc": "Cheapest, fastest, and greenest route options"
        },
        {
            "icon": "🤖",
            "title": "AI Agent",
            "desc": "Voice & text assistant in Urdu and English"
        }
    ]
    
    for i, feature in enumerate([col1, col2, col3, col4]):
        with feature:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">{features[i]['icon']}</div>
                <h3 style="color: #00ff88;">{features[i]['title']}</h3>
                <p>{features[i]['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Live Rate Index
    st.markdown("<h2 style='color: #00ff88; margin-top: 3rem;'>📊 Live Rate Index</h2>", unsafe_allow_html=True)
    
    try:
        rates_response = requests.get(f"{api_url}/api/rates/live?limit=10", timeout=10)
        if rates_response.status_code == 200:
            rates_data = rates_response.json()
            
            if rates_data.get('rates'):
                df = pd.DataFrame(rates_data['rates'])
                
                # Display as cards
                for _, row in df.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{row['origin_city']} → {row['destination_city']}**")
                    with col2:
                        vehicle_names = {1: "Mini-Truck", 2: "Bedford", 3: "20ft", 4: "40ft"}
                        st.markdown(f"{vehicle_names.get(row['vehicle_category'], 'Unknown')}")
                    with col3:
                        st.markdown(f"**Rs {row['median_rate_pkr']:,}**")
                    with col4:
                        st.caption(f"{row['sample_size']} samples")
                    
                    st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
            else:
                st.info("No live rate data available yet. Scrapers are collecting data...")
        else:
            st.error("Failed to fetch live rates")
    except Exception as e:
        st.error(f"Error fetching live rates: {e}")
    
    # How It Works
    st.markdown("<h2 style='color: #00ff88; margin-top: 3rem;'>⚙️ How It Works</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #00ff88;">1. Data Collection</h3>
            <p>Our scrapers collect freight listings from OLX, PakWheels, and other sources every 6 hours.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #00ff88;">2. AI Analysis</h3>
            <p>Machine learning models analyze trends, fuel prices, and seasonal patterns to predict rates.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #00ff88;">3. Optimization</h3>
            <p>Route optimizer calculates cheapest, fastest, and most eco-friendly routes with toll costs.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Vehicle Categories
    st.markdown("<h2 style='color: #00ff88; margin-top: 3rem;'>🚛 Vehicle Categories</h2>", unsafe_allow_html=True)
    
    try:
        vehicles_response = requests.get(f"{api_url}/api/vehicles")
        if vehicles_response.status_code == 200:
            vehicles = vehicles_response.json().get('categories', [])
            
            cols = st.columns(len(vehicles))
            for i, vehicle in enumerate(vehicles):
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <h4 style="color: #00ff88;">{vehicle['name']}</h4>
                        <p><strong>Capacity:</strong> {vehicle['capacity']}</p>
                        <p><strong>Fuel:</strong> {vehicle['fuel_efficiency']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    except:
        st.info("Vehicle data loading...")
    
    # Stats Section
    st.markdown("<h2 style='color: #00ff88; margin-top: 3rem;">📈 Platform Statistics</h2>", unsafe_allow_html=True)
    
    try:
        analytics_response = requests.get(f"{api_url}/api/analytics/summary")
        if analytics_response.status_code == 200:
            stats = analytics_response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Rates", f"{stats.get('total_rates', 0):,}")
            with col2:
                st.metric("Unique Routes", f"{stats.get('unique_routes', 0):,}")
            with col3:
                st.metric("Predictions", f"{stats.get('total_predictions', 0):,}")
            with col4:
                st.metric("Last Updated", "Just now")
    except:
        st.info("Analytics loading...")
    
    # CTA Section
    st.markdown("""
    <div style="background: linear-gradient(90deg, #00ff88 0%, #00cc6a 100%); padding: 2rem; border-radius: 15px; margin-top: 3rem; text-align: center;">
        <h3 style="color: #0a1929; margin-bottom: 1rem;">Ready to optimize your freight operations?</h3>
        <p style="color: #0a1929; margin-bottom: 1.5rem;">
            Start using our rate predictor and route optimizer to save money and time on every shipment.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Links
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Live Rates", use_container_width=True):
            st.switch_page("pages/live_rates.py")
    
    with col2:
        if st.button("🔮 Predict Rates", use_container_width=True):
            st.switch_page("pages/predictor.py")
    
    with col3:
        if st.button("🗺️ Optimize Route", use_container_width=True):
            st.switch_page("pages/optimizer.py")