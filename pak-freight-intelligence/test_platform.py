#!/usr/bin/env python3
"""
Test script to verify the platform is working correctly
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test all API endpoints"""
    
    api_url = "http://localhost:8000"
    
    print("🧪 Testing API Endpoints...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ /health - OK")
        else:
            print(f"❌ /health - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /health - Error: {e}")
    
    # Test cities endpoint
    try:
        response = requests.get(f"{api_url}/api/cities", timeout=5)
        if response.status_code == 200:
            cities = response.json().get('cities', [])
            print(f"✅ /api/cities - OK ({len(cities)} cities)")
        else:
            print(f"❌ /api/cities - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/cities - Error: {e}")
    
    # Test vehicles endpoint
    try:
        response = requests.get(f"{api_url}/api/vehicles", timeout=5)
        if response.status_code == 200:
            vehicles = response.json().get('categories', [])
            print(f"✅ /api/vehicles - OK ({len(vehicles)} categories)")
        else:
            print(f"❌ /api/vehicles - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/vehicles - Error: {e}")
    
    # Test live rates
    try:
        response = requests.get(f"{api_url}/api/rates/live?limit=10", timeout=5)
        if response.status_code == 200:
            rates = response.json().get('rates', [])
            print(f"✅ /api/rates/live - OK ({len(rates)} rates)")
        else:
            print(f"❌ /api/rates/live - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/rates/live - Error: {e}")
    
    # Test prediction
    try:
        payload = {
            "origin": "Karachi",
            "destination": "Lahore",
            "vehicle_category": 4
        }
        response = requests.post(f"{api_url}/api/predict", json=payload, timeout=10)
        if response.status_code == 200:
            prediction = response.json()
            print(f"✅ /api/predict - OK (Rs {prediction.get('current_median', 0):,})")
        else:
            print(f"❌ /api/predict - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/predict - Error: {e}")
    
    # Test route optimization
    try:
        payload = {
            "origin": "Karachi",
            "destination": "Lahore",
            "vehicle_category": 4,
            "has_mtag": True
        }
        response = requests.post(f"{api_url}/api/optimize", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            cheapest = result.get('cheapest', {})
            print(f"✅ /api/optimize - OK (Rs {cheapest.get('total_cost_pkr', 0):,})")
        else:
            print(f"❌ /api/optimize - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/optimize - Error: {e}")

def test_environment():
    """Test environment setup"""
    
    print("\n🔧 Testing Environment...")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major == 3 and python_version.minor >= 11:
        print("✅ Python version is compatible")
    else:
        print("⚠️  Python 3.11+ recommended")
    
    # Check environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'OPENROUTESERVICE_API_KEY']
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} - Set")
        else:
            print(f"❌ {var} - Not set")
    
    # Check if files exist
    important_files = [
        'requirements.txt',
        'backend/main.py',
        'frontend/app.py',
        'scrapers/scrapy.cfg',
        'data/supabase_schema.sql'
    ]
    
    for file in important_files:
        if os.path.exists(file):
            print(f"✅ {file} - Exists")
        else:
            print(f"❌ {file} - Missing")

def test_streamlit():
    """Test Streamlit installation"""
    
    print("\n🎈 Testing Streamlit...")
    print("=" * 50)
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} - Installed")
    except ImportError:
        print("❌ Streamlit not installed")

def test_scrapy():
    """Test Scrapy installation"""
    
    print("\n🕷️  Testing Scrapy...")
    print("=" * 50)
    
    try:
        import scrapy
        print(f"✅ Scrapy {scrapy.__version__} - Installed")
        
        # Test if spiders can be listed
        os.chdir('scrapers')
        import subprocess
        result = subprocess.run(['scrapy', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            spiders = result.stdout.strip().split('\n')
            for spider in spiders:
                if spider:
                    print(f"✅ Spider: {spider}")
        else:
            print("❌ No spiders found")
        os.chdir('..')
        
    except ImportError:
        print("❌ Scrapy not installed")

def generate_report():
    """Generate a test report"""
    
    print("\n📋 Test Report")
    print("=" * 50)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("🚀 Next Steps:")
    print("1. Start the backend: uvicorn backend.main:app --reload")
    print("2. Start the frontend: streamlit run frontend/app.py")
    print("3. Run scrapers: cd scrapers && scrapy crawl olx_freight")
    print("4. Open browser: http://localhost:8501")
    print()
    
    print("🔍 Troubleshooting:")
    print("- If API tests fail, make sure backend is running on port 8000")
    print("- If scrapy tests fail, install with: pip install scrapy")
    print("- If Streamlit tests fail, install with: pip install streamlit")
    print("- Check .env file for missing API keys")

def main():
    """Run all tests"""
    
    print("🚛 Pakistan Freight Intelligence - Platform Test")
    print("=" * 60)
    
    test_environment()
    test_streamlit()
    test_scrapy()
    
    # Only test API if backend might be running
    print("\n💡 Testing API endpoints (make sure backend is running)...")
    test_api_endpoints()
    
    generate_report()

if __name__ == "__main__":
    main()