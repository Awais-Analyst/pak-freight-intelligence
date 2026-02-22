import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
import pandas as pd

class DatabaseService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def health_check(self) -> str:
        """Check database connection"""
        try:
            self.supabase.table('daily_rates').select("count").execute()
            return "healthy"
        except Exception as e:
            return f"unhealthy: {str(e)}"
    
    def get_live_rates(self, limit: int = 20, vehicle_category: Optional[int] = None) -> List[Dict]:
        """Get live median rates for top routes"""
        query = self.supabase.table('daily_rates').select("*")
        
        if vehicle_category:
            query = query.eq('vehicle_category', vehicle_category)
        
        # Get rates from last 7 days
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        query = query.gte('date', seven_days_ago)
        query = query.order('date', desc=True)
        query = query.limit(limit)
        
        result = query.execute()
        return result.data if result.data else []
    
    def get_historical_rates(self, origin: str, destination: str, 
                            vehicle_category: int, days: int = 90) -> pd.DataFrame:
        """Get historical rates for a specific route"""
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        result = self.supabase.table('daily_rates').select("*").eq(
            'origin_city', origin
        ).eq('destination_city', destination).eq(
            'vehicle_category', vehicle_category
        ).gte('date', start_date).order('date').execute()
        
        if result.data:
            df = pd.DataFrame(result.data)
            df['date'] = pd.to_datetime(df['date'])
            return df
        return pd.DataFrame()
    
    def get_fuel_price(self, date: Optional[str] = None) -> Optional[float]:
        """Get fuel price for a specific date or latest"""
        if date:
            result = self.supabase.table('fuel_prices').select("diesel_price_pkr").eq(
                'date', date
            ).execute()
        else:
            result = self.supabase.table('fuel_prices').select("diesel_price_pkr").order(
                'date', desc=True
            ).limit(1).execute()
        
        if result.data:
            return float(result.data[0]['diesel_price_pkr'])
        return None
    
    def get_toll_rate(self, motorway: str, vehicle_category: int) -> Optional[int]:
        """Get toll rate for a motorway and vehicle category"""
        result = self.supabase.table('toll_rates').select("toll_pkr").eq(
            'motorway', motorway
        ).eq('vehicle_category', vehicle_category).order(
            'effective_date', desc=True
        ).limit(1).execute()
        
        if result.data:
            return int(result.data[0]['toll_pkr'])
        return None
    
    def get_cached_route(self, origin: str, destination: str) -> Optional[Dict]:
        """Get cached route from database"""
        result = self.supabase.table('route_cache').select("*").eq(
            'origin', origin
        ).eq('destination', destination).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    def cache_route(self, origin: str, destination: str, distance_km: float, 
                   duration_hours: float, route_data: Dict):
        """Cache route in database"""
        self.supabase.table('route_cache').upsert({
            'origin': origin,
            'destination': destination,
            'distance_km': distance_km,
            'duration_hours': duration_hours,
            'route_data': route_data,
            'cached_at': datetime.now().isoformat()
        }).execute()
    
    def get_current_median_rate(self, origin: str, destination: str, 
                               vehicle_category: int) -> Optional[int]:
        """Get current median rate for a route"""
        # Get rates from last 14 days
        start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        
        result = self.supabase.table('daily_rates').select("median_rate_pkr").eq(
            'origin_city', origin
        ).eq('destination_city', destination).eq(
            'vehicle_category', vehicle_category
        ).gte('date', start_date).execute()
        
        if result.data:
            rates = [int(row['median_rate_pkr']) for row in result.data]
            return int(sum(rates) / len(rates))
        return None
    
    def save_prediction(self, origin: str, destination: str, vehicle_category: int,
                       predicted_rate: int, confidence_lower: int, confidence_upper: int,
                       prediction_date: str, model_version: str):
        """Save prediction to database"""
        self.supabase.table('predictions').insert({
            'origin_city': origin,
            'destination_city': destination,
            'vehicle_category': vehicle_category,
            'predicted_rate_pkr': predicted_rate,
            'confidence_interval_lower': confidence_lower,
            'confidence_interval_upper': confidence_upper,
            'prediction_date': prediction_date,
            'model_version': model_version
        }).execute()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get platform analytics summary"""
        # Count total rates
        rates_count = self.supabase.table('daily_rates').select("count").execute()
        
        # Count unique routes
        unique_routes = self.supabase.table('daily_rates').select(
            "origin_city", "destination_city", "vehicle_category"
        ).execute()
        
        # Count predictions
        predictions_count = self.supabase.table('predictions').select("count").execute()
        
        # Get top routes
        top_routes = self.supabase.table('daily_rates').select(
            "origin_city", "destination_city"
        ).limit(10).execute()
        
        return {
            "total_rates": rates_count.data[0]['count'] if rates_count.data else 0,
            "unique_routes": len(unique_routes.data) if unique_routes.data else 0,
            "total_predictions": predictions_count.data[0]['count'] if predictions_count.data else 0,
            "top_routes": top_routes.data[:5] if top_routes.data else [],
            "last_updated": datetime.now().isoformat()
        }
    
    def aggregate_daily_rates(self):
        """Aggregate raw listings into daily rates"""
        # This would be run by a scheduled job
        # For now, return placeholder
        pass