import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_predictor(api_url):
    """Display rate prediction interface"""
    
    st.markdown("<h1 style='color: #00ff88;'>🔮 AI Rate Predictor</h1>", unsafe_allow_html=True)
    st.markdown("Get AI-powered freight rate predictions for tomorrow and next week")
    
    # Input form
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Get cities from API
            try:
                cities_response = requests.get(f"{api_url}/api/cities", timeout=5)
                if cities_response.status_code == 200:
                    cities = cities_response.json().get('cities', [])
                    origin = st.selectbox("📍 Origin City:", cities, key="origin")
                    destination = st.selectbox("🎯 Destination City:", cities, key="dest")
                else:
                    # Fallback cities
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
                key="vehicle"
            )
            
            # Map to category number
            vehicle_map = {
                "Mini-Truck (1-5 tons)": 1,
                "Bedford (8-14 tons)": 2,
                "20ft Trailer (15-22 tons)": 3,
                "40ft Articulated (30-45 tons)": 4
            }
            vehicle_cat = vehicle_map[vehicle_category]
        
        # Prediction dates
        col1, col2 = st.columns(2)
        with col1:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            st.info(f"📅 Tomorrow: {tomorrow}")
        with col2:
            next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            st.info(f"📅 Next Week: {next_week}")
        
        submitted = st.form_submit_button("🔮 Predict Rates", use_container_width=True)
    
    if submitted:
        if origin == destination:
            st.error("❌ Origin and destination cannot be the same!")
            return
        
        with st.spinner("🤖 AI is analyzing market trends..."):
            try:
                # Make prediction request
                payload = {
                    "origin": origin,
                    "destination": destination,
                    "vehicle_category": vehicle_cat
                }
                
                response = requests.post(f"{api_url}/api/predict", json=payload, timeout=15)
                
                if response.status_code == 200:
                    prediction = response.json()
                    
                    # Display results
                    st.markdown("<h2 style='color: #00ff88; margin-top: 2rem;'>📊 Prediction Results</h2>", unsafe_allow_html=True)
                    
                    # Current rate
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("""
                        <div class="metric-card" style="text-align: center;">
                            <h3 style="color: #00ff88;">Current Rate</h3>
                            <div style="font-size: 2rem; font-weight: bold;">Rs {:,}</div>
                        </div>
                        """.format(prediction['current_median']), unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div class="metric-card" style="text-align: center;">
                            <h3 style="color: #00ff88;">Tomorrow</h3>
                            <div style="font-size: 2rem; font-weight: bold;">Rs {:,}</div>
                            <div style="color: {};">{} {}</div>
                        </div>
                        """.format(
                            prediction['prediction_tomorrow'],
                            "#00ff88" if prediction['prediction_tomorrow'] <= prediction['current_median'] else "#ff6b6b",
                            "▼" if prediction['prediction_tomorrow'] <= prediction['current_median'] else "▲",
                            f"{abs(prediction['prediction_tomorrow'] - prediction['current_median'])/prediction['current_median']*100:.1f}%"
                        ), unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown("""
                        <div class="metric-card" style="text-align: center;">
                            <h3 style="color: #00ff88;">Next Week</h3>
                            <div style="font-size: 2rem; font-weight: bold;">Rs {:,}</div>
                            <div style="color: {};">{} {}</div>
                        </div>
                        """.format(
                            prediction['prediction_7days'],
                            "#00ff88" if prediction['prediction_7days'] <= prediction['current_median'] else "#ff6b6b",
                            "▼" if prediction['prediction_7days'] <= prediction['current_median'] else "▲",
                            f"{abs(prediction['prediction_7days'] - prediction['current_median'])/prediction['current_median']*100:.1f}%"
                        ), unsafe_allow_html=True)
                    
                    # Confidence interval
                    ci = prediction.get('confidence_interval', {})
                    st.markdown("""
                    <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                        <h4 style="color: #00ff88;">📊 Confidence Interval</h4>
                        <p>95% confidence: <strong>Rs {:,}</strong> - <strong>Rs {:,}</strong></p>
                        <p style="font-size: 0.9rem; color: #888;">
                            This means there's a 95% chance the actual rate will fall within this range.
                        </p>
                    </div>
                    """.format(ci.get('lower', 0), ci.get('upper', 0)), unsafe_allow_html=True)
                    
                    # Visualization
                    st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>📈 Rate Forecast</h3>", unsafe_allow_html=True)
                    
                    # Create forecast chart
                    dates = [
                        datetime.now().strftime('%Y-%m-%d'),
                        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                        (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                    ]
                    rates = [
                        prediction['current_median'],
                        prediction['prediction_tomorrow'],
                        prediction['prediction_7days']
                    ]
                    
                    fig = go.Figure()
                    
                    # Add line
                    fig.add_trace(go.Scatter(
                        x=dates, y=rates,
                        mode='lines+markers',
                        name='Predicted Rate',
                        line=dict(color='#00ff88', width=3),
                        marker=dict(size=10, color='#00ff88')
                    ))
                    
                    # Add confidence interval
                    if ci:
                        fig.add_trace(go.Scatter(
                            x=dates + dates[::-1],
                            y=[ci['upper']] * 3 + [ci['lower']] * 3[::-1],
                            fill='toself',
                            fillcolor='rgba(0, 255, 136, 0.1)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name='Confidence Interval',
                            showlegend=True
                        ))
                    
                    fig.update_layout(
                        title=f"Rate Forecast: {origin} → {destination}",
                        xaxis_title="Date",
                        yaxis_title="Rate (PKR)",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Model info
                    with st.expander("ℹ️ About This Prediction"):
                        st.markdown(f"""
                        **Model Information:**
                        - Model Version: {prediction.get('model_version', 'v1.0')}
                        - Route: {origin} → {destination}
                        - Vehicle: {vehicle_category}
                        - Prediction Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                        
                        **How it works:**
                        Our AI uses Prophet + LightGBM ensemble models trained on:
                        - Historical freight rates
                        - Fuel price trends
                        - Seasonal patterns
                        - Economic indicators
                        
                        **Accuracy:**
                        - Typical MAPE: 12-18%
                        - Updates every 6 hours
                        - Improves with more data
                        
                        **Note:** Predictions are estimates. Actual rates may vary based on:
                        - Urgency of shipment
                        - Load availability
                        - Weather conditions
                        - Special events/holidays
                        """)
                
                else:
                    st.error(f"Prediction failed: {response.status_code}")
                    st.json(response.text)
            
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
                st.info("Make sure the API is running.")
    
    # Sample predictions
    st.markdown("<h2 style='color: #00ff88; margin-top: 3rem;'>💡 Sample Predictions</h2>", unsafe_allow_html=True)
    
    sample_routes = [
        {"route": "Karachi → Lahore", "vehicle": "40ft Articulated", "cat": 4},
        {"route": "Lahore → Islamabad", "vehicle": "Bedford", "cat": 2},
        {"route": "Islamabad → Peshawar", "vehicle": "20ft Trailer", "cat": 3},
    ]
    
    cols = st.columns(len(sample_routes))
    
    for i, sample in enumerate(sample_routes):
        with cols[i]:
            if st.button(f"{sample['route']}\n{sample['vehicle']}", key=f"sample_{i}"):
                # Auto-fill the form
                origin_city, dest_city = sample['route'].split(" → ")
                st.session_state['origin'] = origin_city
                st.session_state['dest'] = dest_city
                st.session_state['vehicle'] = sample['vehicle']
                st.rerun()
    
    # Tips
    with st.expander("💡 Tips for Better Predictions"):
        st.markdown("""
        **Getting accurate predictions:**
        
        1. **Choose major cities**: Predictions are more accurate for popular routes
        2. **Consider vehicle type**: Different vehicles have different rate patterns
        3. **Check confidence intervals**: Wider intervals mean less certainty
        4. **Monitor trends**: Use predictions to plan shipments in advance
        
        **Saving money:**
        - Book 2-3 days ahead when possible
        - Avoid peak seasons (Eid, Ramadan)
        - Consider alternative routes
        - Check fuel price trends
        
        **Best practices:**
        - Compare predictions with live rates
        - Use route optimizer for total cost analysis
        - Factor in M-Tag savings on motorways
        """)