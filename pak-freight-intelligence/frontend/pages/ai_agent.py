import streamlit as st
import requests
import json
from datetime import datetime
import speech_recognition as sr
import io
import wave

def show_ai_agent(api_url):
    """Display AI agent interface with voice and text support"""
    
    st.markdown("<h1 style='color: #00ff88;'>🤖 AI Freight Assistant</h1>", unsafe_allow_html=True)
    st.markdown("Ask me about freight rates, route optimization, or anything related to Pakistan's trucking industry")
    
    # Language selection
    col1, col2 = st.columns([3, 1])
    with col2:
        language = st.selectbox("🌐 Language:", ["English", "Urdu", "Roman Urdu"], key="lang")
    
    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="background: rgba(0, 255, 136, 0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; text-align: right;">
                    <strong>You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <strong>🤖 Assistant:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Input methods
    st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>💬 Ask a Question</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your question:",
            placeholder="Ask about rates, routes, or trucking info...",
            key="user_input"
        )
    
    with col2:
        text_submit = st.button("📤 Send Text", use_container_width=True)
    
    with col3:
        voice_button = st.button("🎤 Use Voice", use_container_width=True)
    
    # Voice input handling
    if voice_button:
        with st.spinner("🎤 Listening... Speak now!"):
            try:
                # Initialize speech recognition
                recognizer = sr.Recognizer()
                
                with sr.Microphone() as source:
                    st.info("🎤 Adjusting for ambient noise...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    st.info("🎤 Listening... Speak your question now!")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Try to recognize speech
                try:
                    # Try Urdu first, then English
                    text = recognizer.recognize_google(audio, language="ur-PK")
                    st.success(f"✅ Heard (Urdu): {text}")
                    user_input = text
                except:
                    try:
                        text = recognizer.recognize_google(audio, language="en-US")
                        st.success(f"✅ Heard (English): {text}")
                        user_input = text
                    except:
                        st.error("❌ Could not understand audio. Please try again or type your question.")
                        
            except Exception as e:
                st.error(f"Voice input error: {e}")
                st.info("Make sure your microphone is connected and working.")
    
    # Text input handling
    if text_submit and user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        with st.spinner("🤖 Thinking..."):
            try:
                # Process the query
                response = process_agent_query(user_input, language, api_url)
                
                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Quick actions
    st.markdown("<h3 style='color: #00ff88; margin-top: 2rem;'>⚡ Quick Actions</h3>", unsafe_allow_html=True)
    
    quick_actions = [
        "What's the rate from Karachi to Lahore?",
        "Best route from Islamabad to Peshawar?",
        "Predict rate for tomorrow",
        "How much is the toll on M-2?",
        "Fuel price today?",
        "Compare 20ft vs 40ft trailer costs",
        "Greenest route options?",
        "M-Tag benefits explained"
    ]
    
    cols = st.columns(2)
    
    for i, action in enumerate(quick_actions):
        col = cols[i % 2]
        with col:
            if st.button(action, key=f"quick_{i}", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": action,
                    "timestamp": datetime.now().isoformat()
                })
                
                with st.spinner("🤖 Thinking..."):
                    response = process_agent_query(action, language, api_url)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    st.rerun()
    
    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Agent capabilities
    with st.expander("ℹ️ What I Can Do"):
        st.markdown("""
        **I can help you with:**
        
        🚛 **Rate Information**
        - Current freight rates for any route
        - Rate predictions for tomorrow/next week
        - Historical rate trends
        - Rate comparisons between vehicle types
        
        🗺️ **Route Optimization**
        - Cheapest route suggestions
        - Fastest route options
        - Most eco-friendly routes
        - Toll cost calculations
        - M-Tag benefits
        
        💰 **Cost Analysis**
        - Fuel cost estimates
        - Total trip cost breakdowns
        - Toll vs fuel cost comparisons
        - M-Tag savings calculations
        
        🔍 **General Information**
        - Vehicle specifications
        - Fuel prices
        - Toll rates for motorways
        - Trucking industry tips
        
        **Supported Languages:**
        - English
        - Urdu (اردو)
        - Roman Urdu (Urdu written in English script)
        
        **Examples of what to ask:**
        - "Karachi se Lahore ka rate kya hai?"
        - "Best route from Islamabad to Peshawar"
        - "40ft trailer ka fuel cost kitna hoga?"
        - "M-2 pe toll kitna hai?"
        - "Compare rates for different vehicles"
        
        **Note:** I'm still learning! If I don't understand something, try rephrasing your question.
        I work best with clear, specific questions about freight rates and routes.
        """)

def process_agent_query(query: str, language: str, api_url: str) -> str:
    """Process user query and return AI response"""
    
    query_lower = query.lower()
    
    # Rate prediction queries
    if any(word in query_lower for word in ['rate', 'price', 'cost', 'kiraya', 'قیمت']):
        # Try to extract cities
        cities = extract_cities_from_query(query_lower)
        
        if len(cities) >= 2:
            origin, destination = cities[0], cities[1]
            
            # Try to extract vehicle type
            vehicle_cat = extract_vehicle_from_query(query_lower)
            
            try:
                # Get prediction
                payload = {
                    "origin": origin.title(),
                    "destination": destination.title(),
                    "vehicle_category": vehicle_cat
                }
                
                response = requests.post(f"{api_url}/api/predict", json=payload, timeout=10)
                
                if response.status_code == 200:
                    pred = response.json()
                    
                    return f"""
                    📊 **Rate Prediction: {origin.title()} → {destination.title()}**
                    
                    🚛 **Vehicle:** {get_vehicle_name(vehicle_cat)}
                    
                    💰 **Current Rate:** Rs {pred['current_median']:,}
                    📅 **Tomorrow:** Rs {pred['prediction_tomorrow']:,}
                    📆 **Next Week:** Rs {pred['prediction_7days']:,}
                    
                    📈 **Confidence:** Rs {pred['confidence_interval']['lower']:,} - Rs {pred['confidence_interval']['upper']:,}
                    
                    ℹ️ This prediction is based on current market trends, fuel prices, and historical data.
                    """
                else:
                    return f"I couldn't get the rate prediction right now. Please try again later."
                    
            except Exception as e:
                return f"Sorry, I couldn't fetch the rate data. Error: {str(e)}"
        else:
            return "I can help with rate predictions! Please tell me the origin and destination cities. For example: 'Karachi to Lahore rate for 40ft trailer?'"
    
    # Route optimization queries
    elif any(word in query_lower for word in ['route', 'path', 'rasta', 'road', 'sarak']):
        cities = extract_cities_from_query(query_lower)
        
        if len(cities) >= 2:
            origin, destination = cities[0], cities[1]
            vehicle_cat = extract_vehicle_from_query(query_lower)
            
            try:
                payload = {
                    "origin": origin.title(),
                    "destination": destination.title(),
                    "vehicle_category": vehicle_cat,
                    "has_mtag": True,
                    "optimize_for": "cost"
                }
                
                response = requests.post(f"{api_url}/api/optimize", json=payload, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    cheapest = result.get('cheapest', {})
                    fastest = result.get('fastest', {})
                    
                    return f"""
                    🗺️ **Route Analysis: {origin.title()} → {destination.title()}**
                    
                    💰 **Cheapest Route:**
                    - Route: {cheapest.get('name', 'N/A')}
                    - Distance: {cheapest.get('distance_km', 0):.1f} km
                    - Cost: Rs {cheapest.get('total_cost_pkr', 0):,}
                    - Time: {cheapest.get('duration_hours', 0):.1f} hours
                    
                    ⚡ **Fastest Route:**
                    - Route: {fastest.get('name', 'N/A')}
                    - Distance: {fastest.get('distance_km', 0):.1f} km
                    - Cost: Rs {fastest.get('total_cost_pkr', 0):,}
                    - Time: {fastest.get('duration_hours', 0):.1f} hours
                    
                    🌱 **CO₂ Emissions:** {cheapest.get('co2_emissions_kg', 0):.1f} kg
                    
                    ℹ️ I can also provide more detailed breakdowns or alternative routes if needed!
                    """
                else:
                    return f"I couldn't get route information right now. Please try again."
                    
            except Exception as e:
                return f"Sorry, I couldn't fetch route data. Error: {str(e)}"
        else:
            return "I can help optimize your route! Please tell me the origin and destination cities. For example: 'Best route from Karachi to Lahore?'"
    
    # Toll queries
    elif any(word in query_lower for word in ['toll', 'tax', 'm-tag', 'motorway', 'highway']):
        if 'm-2' in query_lower or 'm2' in query_lower:
            return """
            🛣️ **M-2 Motorway Toll Rates (Islamabad - Lahore)**
            
            💰 **With M-Tag (50% discount):**
            - Mini-Truck: Rs 1,865
            - Bedford: Rs 2,798
            - 20ft Trailer: Rs 3,263
            - 40ft Articulated: Rs 3,730
            
            💸 **Without M-Tag:**
            - Mini-Truck: Rs 3,730
            - Bedford: Rs 5,595
            - 20ft Trailer: Rs 6,525
            - 40ft Articulated: Rs 7,460
            
            ℹ️ M-Tag saves you 50% on all motorway tolls!
            """
        elif 'm-1' in query_lower or 'm1' in query_lower:
            return """
            🛣️ **M-1 Motorway Toll Rates (Islamabad - Peshawar)**
            
            💰 **With M-Tag (50% discount):**
            - Mini-Truck: Rs 1,400
            - Bedford: Rs 2,100
            - 20ft Trailer: Rs 2,450
            - 40ft Articulated: Rs 2,800
            
            💸 **Without M-Tag:**
            - Mini-Truck: Rs 2,800
            - Bedford: Rs 4,200
            - 20ft Trailer: Rs 4,900
            - 40ft Articulated: Rs 5,600
            
            ℹ️ M-Tag saves you 50% on all motorway tolls!
            """
        else:
            return "I have toll information for major motorways! Ask me about M-1 (Islamabad-Peshawar) or M-2 (Islamabad-Lahore) toll rates."
    
    # Fuel price queries
    elif any(word in query_lower for word in ['fuel', 'diesel', 'petrol', 'oil', 'تیل']):
        return """
        ⛽ **Fuel Information**
        
        🛢️ **Current Diesel Price:** ~Rs 280/liter
        
        🚛 **Fuel Efficiency by Vehicle:**
        - Mini-Truck: ~7 km/liter
        - Bedford: ~4.5 km/liter
        - 20ft Trailer: ~3.25 km/liter
        - 40ft Articulated: ~2.75 km/liter
        
        💡 **Tips to save fuel:**
        - Maintain steady speed (80-90 km/h optimal)
        - Avoid excessive idling
        - Regular maintenance
        - Proper tire pressure
        
        📊 **Fuel prices change fortnightly.** I use the latest available price for calculations.
        """
    
    # Vehicle comparison
    elif any(word in query_lower for word in ['compare', 'versus', 'vs', 'diff', 'فرق']):
        return """
        🚛 **Vehicle Comparison**
        
        **Mini-Truck (1-5 tons):**
        - Best for: Small loads, city deliveries
        - Fuel: 7 km/l
        - Rate: Rs 45/km (avg)
        - Examples: Suzuki Carry, Shehzore
        
        **Bedford (8-14 tons):**
        - Best for: Medium loads, intercity
        - Fuel: 4.5 km/l
        - Rate: Rs 65/km (avg)
        - Examples: Bedford trucks, 10-wheelers
        
        **20ft Trailer (15-22 tons):**
        - Best for: Container loads, long distance
        - Fuel: 3.25 km/l
        - Rate: Rs 85/km (avg)
        
        **40ft Articulated (30-45 tons):**
        - Best for: Heavy loads, maximum capacity
        - Fuel: 2.75 km/l
        - Rate: Rs 110/km (avg)
        
        💡 **Choose based on:**
        - Load weight and volume
        - Distance to travel
        - Budget constraints
        - Route accessibility
        """
    
    # M-Tag benefits
    elif any(word in query_lower for word in ['mtag', 'm-tag', 'tag', 'discount', 'savings', 'بچت']):
        return """
        🏷️ **M-Tag Benefits**
        
        💰 **You save 50% on all motorway tolls!**
        
        **Example savings (M-2 Motorway):**
        - 40ft Articulated with M-Tag: Rs 3,730
        - 40ft Articulated without M-Tag: Rs 7,460
        - **You save: Rs 3,730 per trip!**
        
        **How to get M-Tag:**
        1. Visit any M-Tag point on motorways
        2. Provide vehicle documents
        3. Pay Rs 500-1000 (one-time)
        4. Tag installed instantly
        
        **Where M-Tag works:**
        - All Pakistani motorways (M-1, M-2, M-3, etc.)
        - Some national highways
        - Major toll plazas
        
        💡 **Break-even:** If you use motorways regularly, M-Tag pays for itself in 1-2 trips!
        
        🚫 **Without M-Tag:** You pay 50% extra (penalty) at toll plazas
        """
    
    # Green/eco queries
    elif any(word in query_lower for word in ['green', 'eco', 'environment', 'carbon', 'co2', 'پرند']):
        return """
        🌱 **Green Freight Options**
        
        **CO₂ Emissions per route:**
        - Calculated as: Distance × Fuel used × 2.68 kg CO₂/liter
        
        **How to reduce emissions:**
        1. **Choose optimal routes** (I can help!)
        2. **Maintain steady speeds** (80-90 km/h)
        3. **Regular vehicle maintenance**
        4. **Avoid excessive idling**
        5. **Plan efficient loading**
        
        **Green route features:**
        - Shorter distances when possible
        - Less traffic congestion
        - Better road conditions
        - Fewer stops/starts
        
        **Example CO₂ savings:**
        - Karachi to Lahore optimal: ~400 kg CO₂
        - Karachi to Lahore scenic: ~450 kg CO₂
        - **You save: 50 kg CO₂** (equivalent to planting 2-3 trees!)
        
        🌳 **Offset your emissions:** Plant 1 tree per 1000 km traveled
        """
    
    # Greeting/introduction
    elif any(word in query_lower for word in ['hello', 'hi', 'hey', 'salam', 'assalam', 'السلام']):
        return """
        👋 **Hello! Welcome to Pakistan Freight Intelligence**
        
        I'm your AI assistant for all things related to freight and trucking in Pakistan.
        
        **I can help you with:**
        🚛 Freight rates and predictions
        🗺️ Route optimization
        💰 Cost calculations
        🛣️ Toll information
        ⛽ Fuel prices
        🌱 Eco-friendly options
        
        **Just ask me:**
        - "What's the rate from Karachi to Lahore?"
        - "Best route from Islamabad to Peshawar?"
        - "How much is the toll on M-2?"
        - "Predict rates for next week"
        
        I understand English, Urdu, and Roman Urdu!
        """
    
    # Default response
    else:
        return """
        🤔 I didn't quite understand that.
        
        **Try asking me about:**
        🚛 Freight rates (e.g., "Karachi to Lahore rate?")
        🗺️ Route optimization (e.g., "Best route to Peshawar?")
        💰 Toll costs (e.g., "M-2 toll for 40ft?")
        ⛽ Fuel prices and costs
        🏷️ M-Tag benefits
        🌱 Eco-friendly routes
        
        Or simply say "Hello" to get started!
        
        I understand English, Urdu, and Roman Urdu.
        """

def extract_cities_from_query(query: str) -> list:
    """Extract city names from query"""
    
    cities = [
        'Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Peshawar', 'Quetta',
        'Faisalabad', 'Multan', 'Sialkot', 'Gujranwala', 'Sargodha', 'Bahawalpur',
        'Dera Ghazi Khan', 'Hyderabad', 'Sukkur', 'Larkana', 'Mirpurkhas',
        'Mardan', 'Abbottabad', 'Mansehra', 'Swat', 'Malakand', 'Charsadda',
        'Nowshera', 'Kohat', 'Bannu', 'Dera Ismail Khan', 'Tank',
        'Gwadar', 'Turbat', 'Panjgur', 'Khuzdar', 'Hub', 'Lasbela',
        'Rahim Yar Khan', 'Bahawalnagar', 'Vehari', 'Lodhran', 'Khanewal',
        'Okara', 'Pakpattan', 'Arifwala', 'Chichawatni', 'Sahiwal',
        'Kamalia', 'Gojra', 'Toba Tek Singh', 'Jhang', 'Chiniot',
        'Hafizabad', 'Mandi Bahauddin', 'Gujrat', 'Kharian', 'Jhelum',
        'Chakwal', 'Talagang', 'Attock', 'Taxila', 'Wah Cantt',
        'Haripur', 'Karak', 'Hangu', 'Kurram', 'Orakzai',
        'North Waziristan', 'South Waziristan', 'Mohmand', 'Khyber', 'Bajaur'
    ]
    
    found_cities = []
    query_lower = query.lower()
    
    for city in cities:
        if city.lower() in query_lower:
            found_cities.append(city)
    
    return found_cities

def extract_vehicle_from_query(query: str) -> int:
    """Extract vehicle category from query"""
    
    query_lower = query.lower()
    
    # Check for 40ft/articulated
    if any(word in query_lower for word in ['40ft', '40 ft', 'articulated', 'big', 'large']):
        return 4
    
    # Check for 20ft
    elif any(word in query_lower for word in ['20ft', '20 ft', 'container', 'trailer']):
        return 3
    
    # Check for Bedford/10-wheeler
    elif any(word in query_lower for word in ['bedford', '10 wheel', '10-wheel', 'lorry', 'truck']):
        return 2
    
    # Check for mini-truck
    elif any(word in query_lower for word in ['mini', 'pickup', 'suzuki', 'carry', 'small']):
        return 1
    
    # Default to 40ft (most common for long distance)
    return 4

def get_vehicle_name(category: int) -> str:
    """Get vehicle name from category number"""
    
    names = {
        1: "Mini-Truck/Pickup",
        2: "Bedford/10-Wheeler",
        3: "20ft Trailer",
        4: "40ft Articulated"
    }
    
    return names.get(category, "Unknown Vehicle")