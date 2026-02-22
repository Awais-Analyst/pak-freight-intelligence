import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from prophet import Prophet
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

class RatePredictor:
    def __init__(self, db_service):
        self.db = db_service
        self.models = {}
        self.model_version = "v1.0"
        self.models_dir = os.path.join(os.path.dirname(__file__), '../../ml/models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Vehicle specifications
        self.vehicle_specs = {
            1: {"name": "Mini-Truck", "kmpl": 7.0, "capacity_tons": 3},
            2: {"name": "Bedford", "kmpl": 4.5, "capacity_tons": 11},
            3: {"name": "20ft Trailer", "kmpl": 3.25, "capacity_tons": 18.5},
            4: {"name": "40ft Articulated", "kmpl": 2.75, "capacity_tons": 37.5}
        }
    
    def health_check(self) -> str:
        """Check predictor health"""
        try:
            # Try to load a simple model
            test_data = pd.DataFrame({'ds': [datetime.now()], 'y': [50000]})
            model = Prophet(daily_seasonality=False, yearly_seasonality=True)
            model.fit(test_data)
            return "healthy"
        except Exception as e:
            return f"unhealthy: {str(e)}"
    
    def predict(self, origin: str, destination: str, vehicle_category: int, 
                target_date: Optional[str] = None) -> Dict:
        """Predict freight rate for a specific route"""
        
        # Get current median rate
        current_median = self.db.get_current_median_rate(origin, destination, vehicle_category)
        if not current_median:
            # Use fallback based on distance and vehicle category
            current_median = self.estimate_fallback_rate(origin, destination, vehicle_category)
        
        # If no target date, return current rate
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        
        # Get historical data
        hist_data = self.db.get_historical_rates(origin, destination, vehicle_category, days=180)
        
        if len(hist_data) < 10:
            # Not enough data, use simple trend
            prediction_tomorrow = int(current_median * 1.01)  # 1% increase assumption
            prediction_7days = int(current_median * 1.05)     # 5% increase assumption
            
            confidence_interval = {
                "lower": int(current_median * 0.9),
                "upper": int(current_median * 1.1)
            }
        else:
            # Train model and predict
            model_key = f"{origin}_{destination}_{vehicle_category}"
            
            # Prepare features
            features_df = self.prepare_features(hist_data)
            
            # Train ensemble model
            model = self.train_ensemble_model(features_df)
            
            # Make predictions
            prediction_tomorrow = self.predict_date(model, target_dt + timedelta(days=1))
            prediction_7days = self.predict_date(model, target_dt + timedelta(days=7))
            
            confidence_interval = self.calculate_confidence_interval(
                hist_data, prediction_tomorrow
            )
        
        return {
            "origin": origin,
            "destination": destination,
            "vehicle_category": vehicle_category,
            "current_median": current_median,
            "prediction_tomorrow": prediction_tomorrow,
            "prediction_7days": prediction_7days,
            "confidence_interval": confidence_interval,
            "unit": "PKR",
            "model_version": self.model_version
        }
    
    def estimate_fallback_rate(self, origin: str, destination: str, vehicle_category: int) -> int:
        """Estimate rate when no historical data available"""
        
        # Get route distance
        route = self.db.get_cached_route(origin, destination)
        if not route:
            # Use average distances
            distances = {
                ("Karachi", "Lahore"): 1200,
                ("Karachi", "Islamabad"): 1400,
                ("Lahore", "Islamabad"): 300,
                ("Lahore", "Peshawar"): 500,
                ("Karachi", "Peshawar"): 1700,
            }
            distance = distances.get((origin, destination), 800)  # Default 800km
        else:
            distance = route['distance_km']
        
        # Base rates per km (PKR) - estimated from market research
        base_rates_per_km = {
            1: 45,   # Mini-Truck
            2: 65,   # Bedford
            3: 85,   # 20ft
            4: 110   # 40ft
        }
        
        # Calculate estimated rate
        rate_per_km = base_rates_per_km.get(vehicle_category, 60)
        estimated_rate = int(distance * rate_per_km)
        
        return estimated_rate
    
    def prepare_features(self, hist_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML model"""
        
        if hist_data.empty:
            return pd.DataFrame()
        
        # Create features dataframe
        df = hist_data.copy()
        df['ds'] = pd.to_datetime(df['date'])
        df['y'] = df['median_rate_pkr']
        
        # Time features
        df['day_of_week'] = df['ds'].dt.dayofweek
        df['month'] = df['ds'].dt.month
        df['quarter'] = df['ds'].dt.quarter
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Lag features
        df['rate_lag_1'] = df['y'].shift(1)
        df['rate_lag_7'] = df['y'].shift(7)
        df['rate_ma_7'] = df['y'].rolling(window=7).mean()
        df['rate_ma_30'] = df['y'].rolling(window=30).mean()
        
        # Fuel price impact (if available)
        fuel_prices = []
        for date in df['ds']:
            fuel_price = self.db.get_fuel_price(date.strftime('%Y-%m-%d'))
            fuel_prices.append(fuel_price if fuel_price else 280)  # Default
        
        df['fuel_price'] = fuel_prices
        df['fuel_price_change'] = df['fuel_price'].pct_change()
        
        # Seasonal features
        df['is_ramadan'] = 0  # Would need Ramadan dates
        df['is_eid_season'] = 0  # Eid seasons
        
        # Remove rows with NaN
        df = df.dropna()
        
        return df
    
    def train_ensemble_model(self, features_df: pd.DataFrame):
        """Train ensemble model with Prophet + LightGBM"""
        
        if len(features_df) < 10:
            return None
        
        # Train Prophet model
        prophet_model = Prophet(daily_seasonality=False, yearly_seasonality=True)
        prophet_data = features_df[['ds', 'y']].copy()
        prophet_model.fit(prophet_data)
        
        # Train LightGBM for residuals
        # Get Prophet predictions
        prophet_forecast = prophet_model.predict(prophet_data)
        features_df['prophet_pred'] = prophet_forecast['yhat'].values
        features_df['residual'] = features_df['y'] - features_df['prophet_pred']
        
        # Prepare features for LightGBM
        feature_cols = ['day_of_week', 'month', 'quarter', 'is_weekend', 
                       'rate_lag_1', 'rate_lag_7', 'rate_ma_7', 'rate_ma_30',
                       'fuel_price', 'fuel_price_change']
        
        X = features_df[feature_cols].fillna(0)
        y = features_df['residual'].fillna(0)
        
        # Train LightGBM
        lgbm_model = LGBMRegressor(n_estimators=100, random_state=42)
        lgbm_model.fit(X, y)
        
        return {
            'prophet': prophet_model,
            'lgbm': lgbm_model,
            'feature_cols': feature_cols
        }
    
    def predict_date(self, model, target_date: datetime) -> int:
        """Predict rate for a specific date"""
        
        if not model:
            return 0
        
        # Prophet prediction
        future = pd.DataFrame({'ds': [target_date]})
        prophet_pred = model['prophet'].predict(future)
        prophet_value = prophet_pred['yhat'].iloc[0]
        
        # LightGBM correction (using recent features)
        # For simplicity, use average features
        recent_features = {
            'day_of_week': target_date.weekday(),
            'month': target_date.month,
            'quarter': (target_date.month - 1) // 3 + 1,
            'is_weekend': 1 if target_date.weekday() >= 5 else 0,
            'rate_lag_1': prophet_value,
            'rate_lag_7': prophet_value,
            'rate_ma_7': prophet_value,
            'rate_ma_30': prophet_value,
            'fuel_price': 280,  # Current price
            'fuel_price_change': 0
        }
        
        X = pd.DataFrame([recent_features])[model['feature_cols']]
        lgbm_correction = model['lgbm'].predict(X)[0]
        
        # Final prediction
        final_pred = max(0, prophet_value + lgbm_correction)
        return int(final_pred)
    
    def calculate_confidence_interval(self, hist_data: pd.DataFrame, 
                                    prediction: int) -> Dict[str, int]:
        """Calculate confidence interval based on historical volatility"""
        
        if hist_data.empty:
            return {
                "lower": int(prediction * 0.85),
                "upper": int(prediction * 1.15)
            }
        
        # Calculate standard deviation from historical data
        rates = hist_data['median_rate_pkr'].values
        std_dev = np.std(rates)
        
        # 95% confidence interval (approx 2 std dev)
        margin = 2 * std_dev
        
        return {
            "lower": max(0, int(prediction - margin)),
            "upper": int(prediction + margin)
        }
    
    def save_model(self, model, origin: str, destination: str, vehicle_category: int):
        """Save trained model to disk"""
        model_path = os.path.join(
            self.models_dir,
            f"model_{origin}_{destination}_{vehicle_category}.pkl"
        )
        joblib.dump(model, model_path)
    
    def load_model(self, origin: str, destination: str, vehicle_category: int):
        """Load trained model from disk"""
        model_path = os.path.join(
            self.models_dir,
            f"model_{origin}_{destination}_{vehicle_category}.pkl"
        )
        
        if os.path.exists(model_path):
            return joblib.load(model_path)
        return None