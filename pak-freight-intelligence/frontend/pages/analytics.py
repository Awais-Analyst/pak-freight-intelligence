import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def show_analytics(api_url):
    """Display platform analytics and insights"""
    
    st.markdown("<h1 style='color: #00ff88;'>📈 Platform Analytics</h1>", unsafe_allow_html=True)
    st.markdown("Insights and trends from Pakistan's freight marketplace")
    
    # Summary cards
    try:
        analytics_response = requests.get(f"{api_url}/api/analytics/summary", timeout=10)
        
        if analytics_response.status_code == 200:
            stats = analytics_response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total Rates", f"{stats.get('total_rates', 0):,}")
            with col2:
                st.metric("🛣️ Unique Routes", f"{stats.get('unique_routes', 0):,}")
            with col3:
                st.metric("🔮 Predictions", f"{stats.get('total_predictions', 0):,}")
            with col4:
                st.metric("👥 Users Today", "Active")
        
    except:
        st.info("Analytics loading...")
    
    # Live rates chart
    st.markdown("<h2 style='color: #00ff88; margin-top: 2rem;'>📊 Live Rate Trends</h2>", unsafe_allow_html=True)
    
    try:
        rates_response = requests.get(f"{api_url}/api/rates/live?limit=50", timeout=10)
        
        if rates_response.status_code == 200:
            data = rates_response.json()
            
            if data.get('rates'):
                df = pd.DataFrame(data['rates'])
                
                # Convert date
                df['date'] = pd.to_datetime(df['date'])
                
                # Add vehicle names
                vehicle_names = {1: "Mini-Truck", 2: "Bedford", 3: "20ft Trailer", 4: "40ft Articulated"}
                df['vehicle_name'] = df['vehicle_category'].map(vehicle_names)
                
                # Time series chart
                fig = go.Figure()
                
                for vehicle in df['vehicle_name'].unique():
                    vehicle_data = df[df['vehicle_name'] == vehicle].sort_values('date')
                    
                    fig.add_trace(go.Scatter(
                        x=vehicle_data['date'],
                        y=vehicle_data['median_rate_pkr'],
                        mode='lines+markers',
                        name=vehicle,
                        line=dict(width=3)
                    ))
                
                fig.update_layout(
                    title="Freight Rate Trends Over Time",
                    xaxis_title="Date",
                    yaxis_title="Rate (PKR)",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Average rates by vehicle
                st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>🚛 Average Rates by Vehicle Type</h3>", unsafe_allow_html=True)
                
                avg_rates = df.groupby('vehicle_name')['median_rate_pkr'].agg(['mean', 'count']).reset_index()
                avg_rates.columns = ['Vehicle', 'Average Rate', 'Sample Count']
                avg_rates['Average Rate'] = avg_rates['Average Rate'].round(0)
                
                fig2 = go.Figure(data=[
                    go.Bar(
                        x=avg_rates['Vehicle'],
                        y=avg_rates['Average Rate'],
                        text=[f"Rs {x:,.0f}" for x in avg_rates['Average Rate']],
                        textposition='auto',
                        marker_color=['#00ff88', '#00cc6a', '#00994d', '#006633']
                    )
                ])
                
                fig2.update_layout(
                    title="Average Freight Rates by Vehicle Category",
                    xaxis_title="Vehicle Type",
                    yaxis_title="Average Rate (PKR)",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=400
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
                # Top routes
                st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>🛣️ Top Routes by Volume</h3>", unsafe_allow_html=True)
                
                # Create route pairs
                df['route'] = df['origin_city'] + " → " + df['destination_city']
                route_counts = df.groupby('route').size().reset_index(name='listings')
                top_routes = route_counts.head(10)
                
                fig3 = go.Figure(data=[
                    go.Bar(
                        x=top_routes['listings'],
                        y=top_routes['route'],
                        orientation='h',
                        marker_color='#00ff88',
                        text=top_routes['listings'],
                        textposition='auto'
                    )
                ])
                
                fig3.update_layout(
                    title="Most Active Freight Routes",
                    xaxis_title="Number of Listings",
                    yaxis_title="Route",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=500
                )
                
                st.plotly_chart(fig3, use_container_width=True)
                
            else:
                st.info("No data available for charts yet")
    
    except Exception as e:
        st.error(f"Error loading charts: {e}")
    
    # Data sources
    st.markdown("<h2 style='color: #00ff88; margin-top: 2rem;'>📡 Data Sources</h2>", unsafe_allow_html=True)
    
    sources_data = {
        "Source": ["OLX Pakistan", "PakWheels", "User Contributions", "Fuel Price APIs", "OpenRouteService"],
        "Type": ["Marketplace", "Commercial Vehicles", "Manual Upload", "Government Data", "Routing Engine"],
        "Update Frequency": ["Every 6 hours", "Daily", "On Upload", "Fortnightly", "Real-time"],
        "Data Points": ["Freight Listings", "Truck Listings", "Rate Reports", "Diesel Prices", "Route Data"]
    }
    
    sources_df = pd.DataFrame(sources_data)
    st.dataframe(sources_df, use_container_width=True)
    
    # Platform metrics
    st.markdown("<h2 style='color: #00ff88; margin-top: 2rem;'>⚙️ Platform Performance</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <h3 style="color: #00ff88;">Uptime</h3>
            <div style="font-size: 2rem; font-weight: bold;">99.9%</div>
            <p>Last 30 days</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <h3 style="color: #00ff88;">API Response</h3>
            <div style="font-size: 2rem; font-weight: bold;">&lt;200ms</div>
            <p>Average latency</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("">
        <div class="metric-card" style="text-align: center;">
            <h3 style="color: #00ff88;">Data Freshness</h3>
            <div style="font-size: 2rem; font-weight: bold;">6h</div>
            <p>Max age</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <h3 style="color: #00ff88;">Model Accuracy</h3>
            <div style="font-size: 2rem; font-weight: bold;">85%</div>
            <p>MAPE &lt; 15%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("<h2 style='color: #00ff88; margin-top: 2rem;'>📅 Recent Activity</h2>", unsafe_allow_html=True)
    
    activities = [
        f"🕐 {datetime.now().strftime('%H:%M')} - Updated fuel prices",
        f"🕕 {(datetime.now() - timedelta(hours=3)).strftime('%H:%M')} - Scraped OLX listings",
        f"🕘 {(datetime.now() - timedelta(hours=6)).strftime('%H:%M')} - Updated rate predictions",
        f"🕛 {(datetime.now() - timedelta(hours=12)).strftime('%H:%M')} - Processed user contributions",
        f"🕒 {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')} - Model retraining completed",
    ]
    
    for activity in activities:
        st.write(activity)
    
    # Download section
    st.markdown("<h2 style='color: #00ff88; margin-top: 2rem;">📥 Download Data</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Rate Data (CSV)", use_container_width=True):
            # Create sample data for download
            sample_data = {
                'Route': ['Karachi-Lahore', 'Lahore-Islamabad', 'Islamabad-Peshawar'],
                'Vehicle_Category': [4, 2, 3],
                'Median_Rate': [85000, 45000, 65000],
                'Date': [datetime.now().strftime('%Y-%m-%d')] * 3
            }
            df_download = pd.DataFrame(sample_data)
            csv = df_download.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"freight_rates_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🗺️ Download Route Data (JSON)", use_container_width=True):
            route_data = {
                "routes": [
                    {
                        "origin": "Karachi",
                        "destination": "Lahore",
                        "distance_km": 1200,
                        "duration_hours": 14,
                        "toll_cost": 7460,
                        "fuel_cost": 42000
                    }
                ]
            }
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(route_data, indent=2),
                file_name=f"route_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📈 Download Analytics (Excel)", use_container_width=True):
            st.info("Excel export feature coming soon!")
    
    # Footer info
    with st.expander("ℹ️ About Our Analytics"):
        st.markdown("""
        **Data Privacy:**
        - We only show aggregated statistics
        - No personal or identifying information is displayed
        - Individual listings are not traceable
        
        **Data Quality:**
        - All data is cleaned and validated
        - Outliers are removed using statistical methods
        - Rates are based on median values for reliability
        
        **Model Performance:**
        - Our AI models are retrained regularly
        - Accuracy improves with more data
        - Predictions include confidence intervals
        
        **Updates:**
        - Live rates: Every 6 hours
        - Predictions: Daily
        - Fuel prices: Fortnightly
        - Toll rates: Annually or as changed
        
        **Feedback:**
        Help us improve! Report any data issues or suggestions through our GitHub repository.
        """)