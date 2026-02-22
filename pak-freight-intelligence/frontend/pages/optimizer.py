import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def show_optimizer(api_url):
    """Display route optimization interface"""
    
    st.markdown("<h1 style='color: #00ff88;'>🗺️ Route Optimizer</h1>", unsafe_allow_html=True)
    st.markdown("Find the cheapest, fastest, and most eco-friendly routes for your shipments")
    
    # Input form
    with st.form("optimizer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Get cities
            try:
                cities_response = requests.get(f"{api_url}/api/cities", timeout=5)
                if cities_response.status_code == 200:
                    cities = cities_response.json().get('cities', [])
                    origin = st.selectbox("📍 Origin City:", cities, key="origin_opt")
                    destination = st.selectbox("🎯 Destination City:", cities, key="dest_opt")
                else:
                    cities = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Multan", "Faisalabad"]
                    origin = st.selectbox("📍 Origin City:", cities)
                    destination = st.selectbox("🎯 Destination City:", cities)
            except:
                cities = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Multan", "Faisalabad"]
                origin = st.selectbox("📍 Origin City:", cities)
                destination = st.selectbox("🎯 Destination City:", cities)
        
        with col2:
            vehicle_category = st.selectbox(
                "🚛 Vehicle Type:",
                ["Mini-Truck (1-5 tons)", "Bedford (8-14 tons)", "20ft Trailer (15-22 tons)", "40ft Articulated (30-45 tons)"],
                key="vehicle_opt"
            )
            
            vehicle_map = {
                "Mini-Truck (1-5 tons)": 1,
                "Bedford (8-14 tons)": 2,
                "20ft Trailer (15-22 tons)": 3,
                "40ft Articulated (30-45 tons)": 4
            }
            vehicle_cat = vehicle_map[vehicle_category]
            
            has_mtag = st.checkbox("✅ I have M-Tag (50% toll discount)", value=True)
            
            optimize_for = st.selectbox(
                "⚡ Optimize for:",
                ["cost", "time"],
                format_func=lambda x: "Lowest Cost" if x == "cost" else "Fastest Time",
                key="optimize_for"
            )
        
        submitted = st.form_submit_button("🚀 Optimize Route", use_container_width=True)
    
    if submitted:
        if origin == destination:
            st.error("❌ Origin and destination cannot be the same!")
            return
        
        with st.spinner("🗺️ Calculating optimal routes..."):
            try:
                payload = {
                    "origin": origin,
                    "destination": destination,
                    "vehicle_category": vehicle_cat,
                    "has_mtag": has_mtag,
                    "optimize_for": optimize_for
                }
                
                response = requests.post(f"{api_url}/api/optimize", json=payload, timeout=20)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display route summary
                    st.markdown("<h2 style='color: #00ff88; margin-top: 2rem;'>📊 Route Analysis</h2>", unsafe_allow_html=True)
                    
                    analysis = result.get('analysis', {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📏 Distance", f"{analysis.get('distance_km', 0):.1f} km")
                    with col2:
                        st.metric("⏱️ Duration", f"{analysis.get('duration_hours', 0):.1f} hrs")
                    with col3:
                        st.metric("💰 Total Cost", f"Rs {analysis.get('total_cost_pkr', 0):,}")
                    with col4:
                        st.metric("🌱 CO₂", f"{analysis.get('co2_emissions_kg', 0):.1f} kg")
                    
                    # Cost breakdown
                    st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;">💰 Cost Breakdown</h3>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Pie chart
                        fig = go.Figure(data=[go.Pie(
                            labels=['Fuel Cost', 'Toll Cost'],
                            values=[analysis.get('fuel_cost_pkr', 0), analysis.get('toll_cost_pkr', 0)],
                            hole=.3,
                            marker_colors=['#00ff88', '#00cc6a']
                        )])
                        
                        fig.update_layout(
                            title="Cost Breakdown",
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Detailed breakdown
                        st.markdown("""
                        <div class="metric-card">
                            <h4 style="color: #00ff88;">Detailed Breakdown</h4>
                            <p><strong>Fuel Needed:</strong> {:.1f} liters</p>
                            <p><strong>Fuel Cost:</strong> Rs {:,}</p>
                            <p><strong>Toll Cost:</strong> Rs {:,}</p>
                            <p><strong>Current Fuel Price:</strong> Rs {:.2f}/liter</p>
                            <p><strong>M-Tag:</strong> {}</p>
                        </div>
                        """.format(
                            analysis.get('fuel_needed_liters', 0),
                            analysis.get('fuel_cost_pkr', 0),
                            analysis.get('toll_cost_pkr', 0),
                            analysis.get('fuel_price_pkr', 280),
                            "✅ Yes (50% toll discount)" if has_mtag else "❌ No (50% surcharge)"
                        ), unsafe_allow_html=True)
                    
                    # Route options
                    st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>🛣️ Route Options</h3>", unsafe_allow_html=True)
                    
                    routes = result.get('routes', [])
                    
                    for i, route in enumerate(routes):
                        with st.expander(f"🚛 {route['name']}", expanded=i==0):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Distance", f"{route['distance_km']:.1f} km")
                            with col2:
                                st.metric("Duration", f"{route['duration_hours']:.1f} hrs")
                            with col3:
                                st.metric("Total Cost", f"Rs {route['total_cost_pkr']:,}")
                            with col4:
                                st.metric("CO₂", f"{route['co2_emissions_kg']:.1f} kg", 
                                        help="Carbon emissions in kilograms")
                            
                            st.caption(route['description'])
                            
                            # Green badge for lowest CO2
                            if route == result.get('greenest'):
                                st.markdown('<span class="green-badge">🌱 Greenest Option</span>', unsafe_allow_html=True)
                    
                    # Best options
                    st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>🏆 Best Options</h3>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        cheapest = result.get('cheapest', {})
                        st.markdown("""
                        <div class="metric-card" style="border-left: 4px solid #00ff88;">
                            <h4 style="color: #00ff88;">💰 Cheapest</h4>
                            <p><strong>{}</strong></p>
                            <p>Cost: Rs {:,}</p>
                            <p>Distance: {:.1f} km</p>
                        </div>
                        """.format(
                            cheapest.get('name', 'N/A').split('(')[0].strip(),
                            cheapest.get('total_cost_pkr', 0),
                            cheapest.get('distance_km', 0)
                        ), unsafe_allow_html=True)
                    
                    with col2:
                        fastest = result.get('fastest', {})
                        st.markdown("""
                        <div class="metric-card" style="border-left: 4px solid #00cc6a;">
                            <h4 style="color: #00ff88;">⚡ Fastest</h4>
                            <p><strong>{}</strong></p>
                            <p>Time: {:.1f} hours</p>
                            <p>Distance: {:.1f} km</p>
                        </div>
                        """.format(
                            fastest.get('name', 'N/A').split('(')[0].strip(),
                            fastest.get('duration_hours', 0),
                            fastest.get('distance_km', 0)
                        ), unsafe_allow_html=True)
                    
                    with col3:
                        greenest = result.get('greenest', {})
                        st.markdown("""
                        <div class="metric-card" style="border-left: 4px solid #00994d;">
                            <h4 style="color: #00ff88;">🌱 Greenest</h4>
                            <p><strong>{}</strong></p>
                            <p>CO₂: {:.1f} kg</p>
                            <p>Distance: {:.1f} km</p>
                        </div>
                        """.format(
                            greenest.get('name', 'N/A').split('(')[0].strip(),
                            greenest.get('co2_emissions_kg', 0),
                            greenest.get('distance_km', 0)
                        ), unsafe_allow_html=True)
                    
                    # Recommendations
                    st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>💡 Recommendations</h3>", unsafe_allow_html=True)
                    
                    recommendations = []
                    
                    if not has_mtag:
                        recommendations.append("🎫 Get M-Tag to save 50% on toll costs")
                    
                    if cheapest != fastest:
                        time_diff = fastest.get('duration_hours', 0) - cheapest.get('duration_hours', 0)
                        cost_diff = cheapest.get('total_cost_pkr', 0) - fastest.get('total_cost_pkr', 0)
                        
                        if time_diff > 2 and cost_diff > 5000:
                            recommendations.append(f"⏰ Save Rs {cost_diff:,} by taking the cheapest route (only {time_diff:.1f} hours longer)")
                    
                    # Fuel efficiency tips
                    vehicle_specs = {
                        1: {"name": "Mini-Truck", "kmpl": 7.0},
                        2: {"name": "Bedford", "kmpl": 4.5},
                        3: {"name": "20ft Trailer", "kmpl": 3.25},
                        4: {"name": "40ft Articulated", "kmpl": 2.75}
                    }
                    
                    vehicle = vehicle_specs.get(vehicle_cat, {})
                    if vehicle:
                        recommendations.append(f"🛢️ Your {vehicle['name']} gets ~{vehicle['kmpl']} km/l. At current fuel prices, that's ~Rs {280/vehicle['kmpl']:.0f}/km")
                    
                    for rec in recommendations:
                        st.success(rec)
                
                else:
                    st.error(f"Optimization failed: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
    
    # Sample routes
    st.markdown("<h2 style='color: #00ff88; margin-top: 3rem;'>💡 Popular Routes</h2>", unsafe_allow_html=True)
    
    popular_routes = [
        {"origin": "Karachi", "destination": "Lahore", "distance": "~1,200 km"},
        {"origin": "Lahore", "destination": "Islamabad", "distance": "~300 km"},
        {"origin": "Islamabad", "destination": "Peshawar", "distance": "~150 km"},
        {"origin": "Karachi", "destination": "Peshawar", "distance": "~1,700 km"},
        {"origin": "Lahore", "destination": "Multan", "distance": "~350 km"},
        {"origin": "Multan", "destination": "Karachi", "distance": "~900 km"},
    ]
    
    cols = st.columns(3)
    
    for i, route in enumerate(popular_routes[:3]):
        with cols[i]:
            if st.button(f"{route['origin']} → {route['destination']}\n{route['distance']}", 
                        key=f"popular_{i}", use_container_width=True):
                st.session_state['origin_opt'] = route['origin']
                st.session_state['dest_opt'] = route['destination']
                st.rerun()
    
    # Info
    with st.expander("ℹ️ About Route Optimization"):
        st.markdown("""
        **How it works:**
        
        1. **Route Calculation**: Uses OpenRouteService to find optimal paths
        2. **Cost Analysis**: Calculates fuel + toll costs based on vehicle type
        3. **CO₂ Estimation**: Uses standard diesel emission factors (2.68 kg CO₂/liter)
        4. **M-Tag Integration**: Applies 50% toll discount/surcharge automatically
        
        **Vehicle Specifications:**
        - Mini-Truck: 7 km/l, Rs 45/km base rate
        - Bedford: 4.5 km/l, Rs 65/km base rate  
        - 20ft Trailer: 3.25 km/l, Rs 85/km base rate
        - 40ft Articulated: 2.75 km/l, Rs 110/km base rate
        
        **Toll Rates (2025-2026):**
        - M-2 (Islamabad-Lahore): Rs 3,730 - 7,460 depending on vehicle
        - M-1 (Islamabad-Peshawar): Rs 2,800 - 5,600 depending on vehicle
        
        **Note:** Routes are estimates. Actual travel times may vary due to traffic, 
        road conditions, and stops. Always verify with GPS navigation.
        """)