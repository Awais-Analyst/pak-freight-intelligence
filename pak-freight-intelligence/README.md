# 🚛 Pakistan Freight Intelligence Platform

**Pakistan's first public, real-time freight rate intelligence & dynamic cost optimizer platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal.svg)](https://fastapi.tiangolo.com/)

## 🌟 Features

### 📊 Live Rate Intelligence
- **Real-time median rates** scraped from OLX, PakWheels, and public sources
- **Aggregated statistics only** - no personal data exposed
- **Updated every 6 hours** via automated scrapers
- **4 vehicle categories** from Mini-Truck to 40ft Articulated

### 🔮 AI-Powered Predictions
- **Prophet + LightGBM ensemble models** for accurate forecasting
- **Tomorrow & 7-day predictions** with confidence intervals
- **MAPE < 15-18%** target accuracy
- **Considers fuel prices, seasonality, and market trends**

### 🗺️ Route Optimization
- **Multi-objective optimization** (cost, time, CO₂)
- **Real-time toll calculations** with M-Tag integration
- **Fuel cost analysis** based on vehicle efficiency
- **CO₂ emissions tracking** for green logistics

### 🤖 AI Assistant
- **Voice & text support** in Urdu, English, and Roman Urdu
- **Groq Llama-3.1-70B** with function calling
- **Real-time rate queries** and route optimization
- **Industry knowledge base** for trucking information

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Frontend** | Streamlit + Custom CSS | Fast, interactive, dark modern theme |
| **Backend** | FastAPI | High-performance async API |
| **Database** | Supabase Postgres | 500MB free tier, real-time subscriptions |
| **ML Models** | Prophet + LightGBM | Time-series + gradient boosting |
| **Scraping** | Scrapy + Selenium | Robust, scalable data collection |
| **Routing** | OpenRouteService | 2k free requests/day |
| **AI/LLM** | Groq (Llama-3.1-70B) | Millions of tokens free |
| **Analytics** | Umami (Self-hosted) | Privacy-focused analytics |
| **Deployment** | Render + Streamlit Cloud | Free tiers, easy deployment |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Free accounts: Supabase, Groq, OpenRouteService, Render, Streamlit Cloud

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/pak-freight-intelligence.git
cd pak-freight-intelligence
pip install -r requirements.txt
```

### 2. Environment Variables
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Database Setup
- Create Supabase project
- Run `data/supabase_schema.sql` to create tables
- Add connection details to `.env`

### 4. Start Services
```bash
# Terminal 1: FastAPI Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Streamlit Frontend
streamlit run frontend/app.py
```

### 5. Start Scraping
```bash
cd scrapers
scrapy crawl olx_freight
scrapy crawl pakwheels_freight
```

## 📁 Project Structure

```
pak-freight-intelligence/
├── backend/
│   ├── main.py              # FastAPI application
│   └── services/
│       ├── database.py      # Supabase integration
│       ├── predictor.py     # ML prediction engine
│       └── optimizer.py     # Route optimization
├── frontend/
│   ├── app.py              # Streamlit main app
│   └── pages/
│       ├── home.py         # Landing page
│       ├── live_rates.py   # Live rate dashboard
│       ├── predictor.py    # Rate prediction interface
│       ├── optimizer.py    # Route optimization
│       ├── ai_agent.py     # AI chat interface
│       └── analytics.py    # Platform analytics
├── scrapers/
│   ├── scrapy.cfg
│   └── freight_scrapers/
│       ├── spiders/
│       │   ├── olx_spider.py
│       │   └── pakwheels_spider.py
│       └── pipelines.py    # Data processing
├── ml/
│   └── models/             # Trained ML models
├── data/
│   └── supabase_schema.sql # Database schema
├── .github/
│   └── workflows/
│       └── scrape.yml      # Automated scraping
├── requirements.txt
└── README.md
```

## 🎯 Usage Examples

### Get Live Rates
```python
import requests

response = requests.post("http://localhost:8000/api/rates/live", json={
    "limit": 20,
    "vehicle_category": 4  # 40ft Articulated
})
print(response.json())
```

### Predict Rates
```python
response = requests.post("http://localhost:8000/api/predict", json={
    "origin": "Karachi",
    "destination": "Lahore", 
    "vehicle_category": 4
})
print(response.json())
```

### Optimize Route
```python
response = requests.post("http://localhost:8000/api/optimize", json={
    "origin": "Islamabad",
    "destination": "Peshawar",
    "vehicle_category": 2,
    "has_mtag": True
})
print(response.json())
```

## 🚛 Vehicle Categories

| Category | Capacity | Fuel Efficiency | Examples |
|----------|----------|-----------------|----------|
| **1 - Mini-Truck** | 1-5 tons | 6-8 km/l | Suzuki Carry, Shehzore, Pickup |
| **2 - Bedford** | 8-14 tons | 4-5 km/l | Bedford Truck, 10-Wheeler |
| **3 - 20ft Trailer** | 15-22 tons | 3-3.5 km/l | Container Truck, Single Axle |
| **4 - 40ft Articulated** | 30-45 tons | 2.5-3 km/l | Large Container, Articulated |

## 💰 Cost Calculation Logic

### Fuel Cost
```
Fuel Cost = Distance (km) × (1 / kmpl) × Current Diesel Price
```

### Toll Cost
```
Toll Cost = Base Toll × Vehicle Multiplier × M-Tag Factor

M-Tag Factor: 0.5 (with M-Tag) or 1.5 (without M-Tag)
```

### CO₂ Emissions
```
CO₂ (kg) = Distance (km) × (1 / kmpl) × 2.68 kg CO₂/liter
```

## 📊 Data Sources

- **OLX Pakistan**: Freight and transportation listings
- **PakWheels**: Commercial vehicle listings
- **PSO/Shell**: Fortnightly fuel price updates
- **SBP**: USD-PKR exchange rates
- **OpenWeatherMap**: Weather data for route planning
- **User Contributions**: CSV uploads and reports

## 🔒 Privacy & Legal

### Data Privacy
- ✅ **Aggregated statistics only** - no individual listings shown publicly
- ✅ **No personal information** - phone numbers hashed, no names
- ✅ **Privacy-first approach** - data for model training only

### Legal Compliance
- ✅ **Respects robots.txt** where applicable
- ✅ **Conservative scraping** - 5-10 second delays between requests
- ✅ **User-agent identification** - transparent scraping practices
- ✅ **Attribution** - proper credits for data sources

## 🌐 Deployment

### Option 1: Free Deployment (Recommended for Demo)
1. **Backend**: Deploy to Render (free tier)
2. **Frontend**: Deploy to Streamlit Cloud (free)
3. **Database**: Use Supabase (500MB free)
4. **Analytics**: Self-host Umami on Render

### Option 2: Local Development
```bash
# Run everything locally
python backend/main.py
streamlit run frontend/app.py
scrapy crawl olx_freight
```

### Option 3: Production Deployment
- Use paid tiers for better performance
- Set up custom domain
- Configure SSL certificates
- Set up monitoring (Uptime Robot)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute
1. **Report bugs** - Create GitHub issues
2. **Suggest features** - Open feature requests
3. **Submit code** - Fork and create pull requests
4. **Share data** - Upload rate information via CSV
5. **Spread the word** - Share with trucking community

### Development Setup
```bash
# Fork the repository
git clone https://github.com/yourusername/pak-freight-intelligence.git

# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "Add your feature"

# Push and create pull request
git push origin feature/your-feature
```

## 📈 Roadmap

### Phase 1: MVP ✅
- [x] Basic scraping and data collection
- [x] Rate prediction models
- [x] Route optimization
- [x] Simple web interface
- [x] AI agent integration

### Phase 2: Enhanced Features
- [ ] Mobile app (React Native)
- [ ] Real-time notifications
- [ ] Advanced filtering and search
- [ ] Historical data export
- [ ] Multi-language support

### Phase 3: Community Features
- [ ] User reviews and ratings
- [ ] Verified transporter profiles
- [ ] Load matching platform
- [ ] Community forums
- [ ] Industry news integration

## 📞 Support

### For Truckers
- **Live Chat**: Available on the platform
- **WhatsApp**: +92-XXX-XXXXXXX (coming soon)
- **Email**: support@freight-intelligence.pk

### For Developers
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: [Wiki](https://github.com/yourusername/pak-freight-intelligence/wiki)
- **API Docs**: Available at `/docs` when running locally

### For Partners
- **Business Inquiries**: partners@freight-intelligence.pk
- **Data Partnerships**: data@freight-intelligence.pk
- **Media**: media@freight-intelligence.pk

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Open Source Community** - For amazing free tools and libraries
- **Pakistani Trucking Community** - For inspiring this project
- **Contributors** - Everyone who helped build and test the platform
- **Data Sources** - OLX, PakWheels, and others for public data

## 🌟 Star History

If this project helped you, please give it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/pak-freight-intelligence&type=Date)](https://star-history.com/#yourusername/pak-freight-intelligence&Date)

---

**Made with ❤️ for Pakistan's trucking community**

*This is a community-driven project aimed at modernizing Pakistan's freight industry through technology and data transparency.*