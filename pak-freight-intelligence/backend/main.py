from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from .services.predictor import RatePredictor
from .services.optimizer import RouteOptimizer
from .services.database import DatabaseService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Pakistan Freight Intelligence API",
    description="Real-time freight rate intelligence and route optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class RatePredictionRequest(BaseModel):
    origin: str
    destination: str
    vehicle_category: int  # 1-4
    date: Optional[str] = None  # YYYY-MM-DD, defaults to today

class RatePredictionResponse(BaseModel):
    origin: str
    destination: str
    vehicle_category: int
    current_median: int
    prediction_tomorrow: Optional[int]
    prediction_7days: Optional[int]
    confidence_interval: dict

class RouteOptimizationRequest(BaseModel):
    origin: str
    destination: str
    vehicle_category: int
    has_mtag: bool = True
    optimize_for: str = "cost"  # "cost" or "time"

class RouteOptimizationResponse(BaseModel):
    routes: List[dict]
    cheapest: dict
    fastest: dict
    greenest: dict

class LiveRatesResponse(BaseModel):
    rates: List[dict]
    last_updated: str

# Initialize services
db_service = DatabaseService()
predictor = RatePredictor(db_service)
optimizer = RouteOptimizer(db_service)

@app.get("/")
async def root():
    return {
        "message": "Pakistan Freight Intelligence API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": db_service.health_check(),
            "predictor": predictor.health_check(),
            "optimizer": optimizer.health_check()
        }
    }

@app.get("/api/rates/live", response_model=LiveRatesResponse)
async def get_live_rates(
    limit: int = 20,
    vehicle_category: Optional[int] = None
):
    """Get live median rates for top routes"""
    try:
        rates = db_service.get_live_rates(limit=limit, vehicle_category=vehicle_category)
        return LiveRatesResponse(
            rates=rates,
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict", response_model=RatePredictionResponse)
async def predict_rate(request: RatePredictionRequest):
    """Predict freight rates for a specific route"""
    try:
        prediction = predictor.predict(
            origin=request.origin,
            destination=request.destination,
            vehicle_category=request.vehicle_category,
            target_date=request.date
        )
        
        return RatePredictionResponse(
            origin=prediction['origin'],
            destination=prediction['destination'],
            vehicle_category=prediction['vehicle_category'],
            current_median=prediction['current_median'],
            prediction_tomorrow=prediction.get('prediction_tomorrow'),
            prediction_7days=prediction.get('prediction_7days'),
            confidence_interval=prediction.get('confidence_interval', {})
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize", response_model=RouteOptimizationResponse)
async def optimize_route(request: RouteOptimizationRequest):
    """Optimize route with cost, time, and CO2 analysis"""
    try:
        result = optimizer.optimize(
            origin=request.origin,
            destination=request.destination,
            vehicle_category=request.vehicle_category,
            has_mtag=request.has_mtag,
            optimize_for=request.optimize_for
        )
        
        return RouteOptimizationResponse(
            routes=result['routes'],
            cheapest=result['cheapest'],
            fastest=result['fastest'],
            greenest=result['greenest']
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cities")
async def get_cities():
    """Get list of available cities"""
    return {
        "cities": [
            "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Quetta",
            "Faisalabad", "Multan", "Sialkot", "Gujranwala", "Sargodha", "Bahawalpur",
            "Dera Ghazi Khan", "Hyderabad", "Sukkur", "Larkana", "Mirpurkhas",
            "Mardan", "Abbottabad", "Mansehra", "Swat", "Malakand", "Charsadda",
            "Nowshera", "Kohat", "Bannu", "Dera Ismail Khan", "Tank",
            "Gwadar", "Turbat", "Panjgur", "Khuzdar", "Hub", "Lasbela",
            "Rahim Yar Khan", "Bahawalnagar", "Vehari", "Lodhran", "Khanewal",
            "Okara", "Pakpattan", "Arifwala", "Chichawatni", "Sahiwal",
            "Kamalia", "Gojra", "Toba Tek Singh", "Jhang", "Chiniot",
            "Hafizabad", "Mandi Bahauddin", "Gujrat", "Kharian", "Jhelum",
            "Chakwal", "Talagang", "Attock", "Taxila", "Wah Cantt",
            "Haripur", "Karak", "Hangu", "Kurram", "Orakzai",
            "North Waziristan", "South Waziristan", "Mohmand", "Khyber", "Bajaur"
        ]
    }

@app.get("/api/vehicles")
async def get_vehicle_categories():
    """Get vehicle categories with details"""
    return {
        "categories": [
            {
                "id": 1,
                "name": "Mini-Truck / Pickup",
                "capacity": "1-5 tons",
                "fuel_efficiency": "6-8 km/l",
                "examples": ["Suzuki Carry", "Shehzore", "Pickup"]
            },
            {
                "id": 2,
                "name": "Bedford / 10-Wheeler",
                "capacity": "8-14 tons",
                "fuel_efficiency": "4-5 km/l",
                "examples": ["Bedford Truck", "10-Wheeler Lorry"]
            },
            {
                "id": 3,
                "name": "20-ft Trailer",
                "capacity": "15-22 tons",
                "fuel_efficiency": "3-3.5 km/l",
                "examples": ["20ft Container Truck", "Single Axle Trailer"]
            },
            {
                "id": 4,
                "name": "40-ft Articulated",
                "capacity": "30-45 tons",
                "fuel_efficiency": "2.5-3 km/l",
                "examples": ["40ft Container", "Articulated Lorry"]
            }
        ]
    }

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get platform analytics summary"""
    try:
        summary = db_service.get_analytics_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)