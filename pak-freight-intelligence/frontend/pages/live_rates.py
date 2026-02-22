import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def show_live_rates(api_url):
    """Display live freight rates"""
    
    st.markdown("<h1 style='color: #00ff88;'>📊 Live Freight Rates</h1>", unsafe_allow_html=True)
    st.markdown("Real-time median rates from marketplace data")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vehicle_filter = st.selectbox(
            "Filter by Vehicle:",
            ["All", "Mini-Truck", "Bedford", "20ft Trailer", "40ft Articulated"],
            key="vehicle_filter"
        )
    
    with col2:
        limit = st.slider("Number of routes:", 10, 100, 20)
    
    with col3:
        refresh = st.button("🔄 Refresh Data")
    
    # Fetch live rates
    try:
        vehicle_category = None
        if vehicle_filter != "All":
            vehicle_map = {"Mini-Truck": 1, "Bedford": 2, "20ft Trailer": 3, "40ft Articulated": 4}
            vehicle_category = vehicle_map.get(vehicle_filter)
        
        params = {"limit": limit}
        if vehicle_category:
            params["vehicle_category"] = vehicle_category
        
        response = requests.get(f"{api_url}/api/rates/live", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('rates'):
                df = pd.DataFrame(data['rates'])
                
                # Add vehicle names
                vehicle_names = {1: "Mini-Truck", 2: "Bedford", 3: "20ft Trailer", 4: "40ft Articulated"}
                df['vehicle_name'] = df['vehicle_category'].map(vehicle_names)
                
                # Display summary stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Routes", len(df))
                with col2:
                    avg_rate = df['median_rate_pkr'].mean()
                    st.metric("Average Rate", f"Rs {avg_rate:,.0f}")
                with col3:
                    max_rate = df['median_rate_pkr'].max()
                    st.metric("Highest Rate", f"Rs {max_rate:,.0f}")
                with col4:
                    min_rate = df['median_rate_pkr'].min()
                    st.metric("Lowest Rate", f"Rs {min_rate:,.0f}")
                
                # Charts
                st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>📈 Rate Analysis</h3>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Rates by vehicle category
                    fig1 = go.Figure()
                    
                    for vehicle in df['vehicle_name'].unique():
                        vehicle_data = df[df['vehicle_name'] == vehicle]
                        fig1.add_trace(go.Box(
                            y=vehicle_data['median_rate_pkr'],
                            name=vehicle,
                            boxpoints='outliers'
                        ))
                    
                    fig1.update_layout(
                        title="Rate Distribution by Vehicle Type",
                        xaxis_title="Vehicle Type",
                        yaxis_title="Rate (PKR)",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Sample size distribution
                    fig2 = px.scatter(
                        df, 
                        x='sample_size', 
                        y='median_rate_pkr',
                        color='vehicle_name',
                        size='sample_size',
                        title="Rate vs Sample Size",
                        template="plotly_dark"
                    )
                    fig2.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Data table
                st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>📋 Detailed Rates</h3>", unsafe_allow_html=True)
                
                # Format dataframe for display
                display_df = df[['origin_city', 'destination_city', 'vehicle_name', 
                               'median_rate_pkr', 'avg_rate_pkr', 'sample_size', 'date']].copy()
                
                display_df.columns = ['Origin', 'Destination', 'Vehicle', 'Median Rate', 
                                    'Average Rate', 'Samples', 'Date']
                
                # Format numbers
                display_df['Median Rate'] = display_df['Median Rate'].apply(lambda x: f"Rs {x:,}")
                display_df['Average Rate'] = display_df['Average Rate'].apply(lambda x: f"Rs {x:,}")
                
                st.dataframe(display_df, use_container_width=True)
                
                # Download button
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=csv,
                    file_name=f"freight_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.info("No rate data available. Scrapers are collecting data...")
                
                # Show sample data structure
                sample_data = {
                    'Route': ['Karachi → Lahore', 'Lahore → Islamabad', 'Islamabad → Peshawar'],
                    'Vehicle': ['40ft Articulated', 'Bedford', '20ft Trailer'],
                    'Rate (PKR)': ['Rs 85,000', 'Rs 45,000', 'Rs 65,000'],
                    'Status': ['Collecting...', 'Collecting...', 'Collecting...']
                }
                st.dataframe(pd.DataFrame(sample_data), use_container_width=True)
        else:
            st.error(f"Failed to fetch rates. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        st.info("Make sure the API is running. If you're developing locally, start the FastAPI server first.")
    
    # Info section
    with st.expander("ℹ️ About Live Rates"):
        st.markdown("""
        **How it works:**
        - Our scrapers collect freight listings from OLX, PakWheels, and other sources every 6 hours
        - Data is cleaned, classified by vehicle type, and aggregated
        - Median rates are calculated for each route and vehicle category
        - Only aggregated statistics are shown publicly (no personal data)
        
        **Data Sources:**
        - OLX Pakistan (freight/transportation listings)
        - PakWheels (commercial vehicles)
        - User contributions (CSV uploads)
        
        **Vehicle Categories:**
        1. **Mini-Truck/Pickup (1-5 tons)**: Suzuki Carry, Shehzore, pickups
        2. **Bedford/10-Wheeler (8-14 tons)**: Bedford trucks, 10-wheeler lorries
        3. **20-ft Trailer (15-22 tons)**: Container trucks, single axle trailers
        4. **40-ft Articulated (30-45 tons)**: Large container trucks, articulated lorries
        
        **Note:** Rates are indicative and may vary based on load, urgency, and market conditions.
        Always negotiate final rates directly with transport providers.
        """)