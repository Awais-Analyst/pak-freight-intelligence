#!/usr/bin/env python3
"""
Update ML predictions for freight rates
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from backend.services.predictor import RatePredictor
from backend.services.database import DatabaseService

def update_predictions():
    """Update rate predictions for major routes"""
    
    db = DatabaseService()
    predictor = RatePredictor(db)
    
    print("Updating rate predictions...")
    
    # Major routes to predict
    routes = [
        {"origin": "Karachi", "destination": "Lahore", "vehicle_category": 4},
        {"origin": "Lahore", "destination": "Islamabad", "vehicle_category": 2},
        {"origin": "Islamabad", "destination": "Peshawar", "vehicle_category": 3},
        {"origin": "Karachi", "destination": "Peshawar", "vehicle_category": 4},
        {"origin": "Multan", "destination": "Karachi", "vehicle_category": 3},
        {"origin": "Faisalabad", "destination": "Karachi", "vehicle_category": 3},
        {"origin": "Lahore", "destination": "Multan", "vehicle_category": 2},
    ]
    
    for route in routes:
        try:
            # Make prediction
            prediction = predictor.predict(
                origin=route['origin'],
                destination=route['destination'],
                vehicle_category=route['vehicle_category']
            )
            
            # Save prediction to database
            db.save_prediction(
                origin=route['origin'],
                destination=route['destination'],
                vehicle_category=route['vehicle_category'],
                predicted_rate=prediction['prediction_tomorrow'],
                confidence_lower=prediction['confidence_interval']['lower'],
                confidence_upper=prediction['confidence_interval']['upper'],
                prediction_date=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                model_version=prediction['model_version']
            )
            
            print(f"✓ {route['origin']} → {route['destination']} (Cat {route['vehicle_category']}): Rs {prediction['prediction_tomorrow']:,}")
            
        except Exception as e:
            print(f"✗ Error predicting {route['origin']} → {route['destination']}: {e}")
    
    print(f"\n✅ Prediction update completed for {len(routes)} routes")

if __name__ == "__main__":
    update_predictions()