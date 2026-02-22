import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import openrouteservice
from openrouteservice import convert
import requests

class RouteOptimizer:
    def __init__(self, db_service):
        self.db = db_service
        self.ors_key = os.getenv("OPENROUTESERVICE_API_KEY", "your-key-here")
        self.ors_client = openrouteservice.Client(key=self.ors_key)
        
        # Vehicle specifications
        self.vehicle_specs = {
            1: {
                "name": "Mini-Truck / Pickup",
                "kmpl": 7.0,
                "capacity_tons": 3,
                "toll_multiplier": 1.0
            },
            2: {
                "name": "Bedford / 10-Wheeler", 
                "kmpl": 4.5,
                "capacity_tons": 11,
                "toll_multiplier": 1.5
            },
            3: {
                "name": "20-ft Trailer",
                "kmpl": 3.25,
                "capacity_tons": 18.5,
                "toll_multiplier": 1.75
            },
            4: {
                "name": "40-ft Articulated",
                "kmpl": 2.75,
                "capacity_tons": 37.5,
                "toll_multiplier": 2.0
            }
        }
        
        # CO2 emission factor (kg CO2 per liter of diesel)
        self.co2_factor = 2.68
        
        # Motorway mappings
        self.motorways = {
            "M-1": {
                "route": "Islamabad - Peshawar",
                "cities": ["Islamabad", "Rawalpindi", "Peshawar", "Nowshera"]
            },
            "M-2": {
                "route": "Islamabad - Lahore", 
                "cities": ["Islamabad", "Rawalpindi", "Lahore", "Gujranwala", "Sheikhupura"]
            },
            "M-3": {
                "route": "Lahore - Multan",
                "cities": ["Lahore", "Multan", "Khanewal", "Vehari"]
            },
            "M-4": {
                "route": "Pindi Bhattian - Faisalabad",
                "cities": ["Pindi Bhattian", "Faisalabad", "Jhang"]
            },
            "M-5": {
                "route": "Multan - Sukkur",
                "cities": ["Multan", "Sukkur", "Bahawalpur", "Rahim Yar Khan"]
            },
            "M-6": {
                "route": "Sukkur - Hyderabad",
                "cities": ["Sukkur", "Hyderabad", "Larkana", "Nawabshah"]
            },
            "M-7": {
                "route": "Karachi - Hub",
                "cities": ["Karachi", "Hub", "Lasbela"]
            },
            "M-8": {
                "route": "Ratodero - Gwadar",
                "cities": ["Ratodero", "Gwadar", "Turbat", "Panjgur", "Khuzdar"]
            },
            "M-9": {
                "route": "Hyderabad - Karachi",
                "cities": ["Hyderabad", "Karachi", "Thatta"]
            }
        }
    
    def health_check(self) -> str:
        """Check optimizer health"""
        try:
            # Test with a simple coordinate
            coords = [[74.3587, 31.5204], [73.0479, 33.6844]]  # Lahore to Islamabad
            routes = self.ors_client.directions(coords, profile='driving-hgv')
            return "healthy"
        except Exception as e:
            return f"unhealthy: {str(e)}"
    
    def optimize(self, origin: str, destination: str, vehicle_category: int,
                has_mtag: bool = True, optimize_for: str = "cost") -> Dict:
        """Optimize route with cost, time, and CO2 analysis"""
        
        # Get route from cache or API
        route_data = self.get_route(origin, destination)
        if not route_data:
            raise ValueError(f"Could not find route from {origin} to {destination}")
        
        distance_km = route_data['distance_km']
        duration_hours = route_data['duration_hours']
        
        # Get current fuel price
        fuel_price = self.db.get_fuel_price()
        if not fuel_price:
            fuel_price = 280  # Default fallback
        
        # Calculate costs
        vehicle_spec = self.vehicle_specs[vehicle_category]
        
        # Fuel cost
        fuel_needed = distance_km / vehicle_spec['kmpl']
        fuel_cost = fuel_needed * fuel_price
        
        # Toll cost
        toll_cost = self.calculate_toll_cost(
            origin, destination, vehicle_category, has_mtag
        )
        
        # Total cost
        total_cost = fuel_cost + toll_cost
        
        # CO2 emissions
        co2_emissions = fuel_needed * self.co2_factor
        
        # Create route options
        routes = self.generate_route_options(
            origin, destination, vehicle_category, has_mtag
        )
        
        # Find best routes
        cheapest = min(routes, key=lambda x: x['total_cost'])
        fastest = min(routes, key=lambda x: x['duration_hours'])
        greenest = min(routes, key=lambda x: x['co2_emissions'])
        
        return {
            "routes": routes,
            "cheapest": cheapest,
            "fastest": fastest,
            "greenest": greenest,
            "analysis": {
                "distance_km": distance_km,
                "duration_hours": duration_hours,
                "fuel_needed_liters": round(fuel_needed, 2),
                "fuel_cost_pkr": int(fuel_cost),
                "toll_cost_pkr": int(toll_cost),
                "total_cost_pkr": int(total_cost),
                "co2_emissions_kg": round(co2_emissions, 2),
                "fuel_price_pkr": fuel_price,
                "vehicle_category": vehicle_category,
                "has_mtag": has_mtag
            }
        }
    
    def get_route(self, origin: str, destination: str) -> Optional[Dict]:
        """Get route from cache or API"""
        
        # Check cache first
        cached = self.db.get_cached_route(origin, destination)
        if cached:
            return {
                'distance_km': float(cached['distance_km']),
                'duration_hours': float(cached['duration_hours']),
                'route_data': cached['route_data']
            }
        
        # Get from OpenRouteService
        try:
            # Geocode cities (simplified - in production use proper geocoding)
            city_coords = self.get_city_coordinates(origin, destination)
            if not city_coords:
                return None
            
            # Get route
            coords = [city_coords['origin'], city_coords['destination']]
            routes = self.ors_client.directions(
                coords, 
                profile='driving-hgv',
                format='geojson'
            )
            
            # Extract route info
            route = routes['features'][0]
            distance_m = route['properties']['segments'][0]['distance']
            duration_s = route['properties']['segments'][0]['duration']
            
            distance_km = distance_m / 1000
            duration_hours = duration_s / 3600
            
            # Cache the route
            self.db.cache_route(
                origin=origin,
                destination=destination,
                distance_km=distance_km,
                duration_hours=duration_hours,
                route_data=route
            )
            
            return {
                'distance_km': distance_km,
                'duration_hours': duration_hours,
                'route_data': route
            }
            
        except Exception as e:
            print(f"Error getting route: {e}")
            return None
    
    def get_city_coordinates(self, origin: str, destination: str) -> Optional[Dict]:
        """Get coordinates for cities (simplified mapping)"""
        
        # Major city coordinates
        city_coords = {
            "Karachi": [67.0011, 24.8607],
            "Lahore": [74.3587, 31.5204],
            "Islamabad": [73.0479, 33.6844],
            "Rawalpindi": [73.0479, 33.6844],
            "Peshawar": [71.5241, 34.0150],
            "Quetta": [66.9987, 30.1798],
            "Faisalabad": [73.0945, 31.4180],
            "Multan": [71.4937, 30.1575],
            "Sialkot": [74.5311, 32.4927],
            "Gujranwala": [74.1881, 32.1877],
            "Sargodha": [72.6711, 32.0836],
            "Bahawalpur": [71.6801, 29.3956],
            "Dera Ghazi Khan": [70.6351, 30.0458],
            "Hyderabad": [68.3737, 25.3969],
            "Sukkur": [68.8578, 27.7052],
            "Larkana": [68.2120, 27.5586],
            "Mirpurkhas": [69.0118, 25.5267],
            "Mardan": [72.0439, 34.1958],
            "Abbottabad": [73.2145, 34.1463],
            "Mansehra": [73.3532, 34.3337],
            "Swat": [72.1750, 35.3620],
            "Gwadar": [62.3254, 25.1266],
            "Turbat": [63.0672, 26.0034],
            "Khuzdar": [66.6118, 27.8009],
            "Hub": [63.3495, 25.0677],
            "Rahim Yar Khan": [70.3003, 28.4199],
            "Bahawalnagar": [73.2536, 29.9986],
            "Vehari": [72.3506, 30.0473],
            "Lodhran": [71.6317, 29.5405],
            "Khanewal": [71.9331, 30.3006],
            "Okara": [73.4511, 30.8074],
            "Pakpattan": [73.3885, 30.0800],
            "Arifwala": [73.0579, 30.2941],
            "Chichawatni": [72.6895, 30.5300],
            "Sahiwal": [73.1111, 30.6667],
            "Kamalia": [72.6458, 30.7300],
            "Gojra": [72.6833, 31.1500],
            "Toba Tek Singh": [72.4833, 30.9700],
            "Jhang": [72.3167, 31.2700],
            "Chiniot": [72.9833, 31.7200],
            "Hafizabad": [73.6833, 32.0700],
            "Mandi Bahauddin": [73.4833, 32.5800],
            "Gujrat": [74.0833, 32.5700],
            "Kharian": [73.9000, 32.8100],
            "Jhelum": [73.7333, 32.9333],
            "Chakwal": [72.8500, 32.9300],
            "Talagang": [72.4167, 32.9300],
            "Attock": [72.3667, 33.7667],
            "Taxila": [72.8000, 33.7500],
            "Wah Cantt": [72.7500, 33.8000],
            "Haripur": [72.9333, 33.9833],
            "Karak": [71.1000, 33.1167],
            "Hangu": [71.0500, 33.5333],
            "Charsadda": [71.7333, 34.1500],
            "Nowshera": [71.9833, 33.9833],
            "Kohat": [71.4333, 33.5833],
            "Bannu": [70.6000, 32.9833],
            "Dera Ismail Khan": [70.9000, 31.8333],
            "Tank": [70.3833, 32.2167]
        }
        
        if origin not in city_coords or destination not in city_coords:
            return None
        
        return {
            'origin': city_coords[origin],
            'destination': city_coords[destination]
        }
    
    def calculate_toll_cost(self, origin: str, destination: str, 
                          vehicle_category: int, has_mtag: bool) -> float:
        """Calculate toll cost for a route"""
        
        # Determine which motorways are used
        motorways_used = self.get_motorways_for_route(origin, destination)
        
        total_toll = 0
        for motorway in motorways_used:
            toll = self.db.get_toll_rate(motorway, vehicle_category)
            if toll:
                total_toll += toll
        
        # Apply M-Tag penalty if no M-Tag
        if not has_mtag:
            total_toll *= 1.5
        
        return total_toll
    
    def get_motorways_for_route(self, origin: str, destination: str) -> List[str]:
        """Determine which motorways are likely used for a route"""
        
        # Simple heuristic based on city pairs
        route_cities = {origin, destination}
        used_motorways = []
        
        for motorway, info in self.motorways.items():
            if any(city in route_cities for city in info['cities']):
                used_motorways.append(motorway)
        
        return used_motorways
    
    def generate_route_options(self, origin: str, destination: str, 
                             vehicle_category: int, has_mtag: bool) -> List[Dict]:
        """Generate multiple route options"""
        
        # Get main route
        main_route = self.get_route(origin, destination)
        if not main_route:
            return []
        
        distance_km = main_route['distance_km']
        duration_hours = main_route['duration_hours']
        
        # Get current fuel price
        fuel_price = self.db.get_fuel_price() or 280
        vehicle_spec = self.vehicle_specs[vehicle_category]
        
        # Calculate costs
        fuel_needed = distance_km / vehicle_spec['kmpl']
        fuel_cost = fuel_needed * fuel_price
        toll_cost = self.calculate_toll_cost(origin, destination, vehicle_category, has_mtag)
        total_cost = fuel_cost + toll_cost
        co2_emissions = fuel_needed * self.co2_factor
        
        # Generate options with slight variations
        options = []
        
        # Main route (optimal)
        options.append({
            "name": f"{origin} → {destination} (Optimal)",
            "distance_km": round(distance_km, 1),
            "duration_hours": round(duration_hours, 1),
            "fuel_cost_pkr": int(fuel_cost),
            "toll_cost_pkr": int(toll_cost),
            "total_cost_pkr": int(total_cost),
            "co2_emissions_kg": round(co2_emissions, 2),
            "route_type": "optimal",
            "description": "Fastest and most cost-effective route"
        })
        
        # Alternative route (slightly longer, maybe cheaper tolls)
        alt_distance = distance_km * 1.1  # 10% longer
        alt_duration = duration_hours * 1.15  # 15% longer
        alt_fuel_needed = alt_distance / vehicle_spec['kmpl']
        alt_fuel_cost = alt_fuel_needed * fuel_price
        alt_toll_cost = toll_cost * 0.8  # 20% cheaper tolls
        alt_total_cost = alt_fuel_cost + alt_toll_cost
        alt_co2 = alt_fuel_needed * self.co2_factor
        
        options.append({
            "name": f"{origin} → {destination} (Alternative)",
            "distance_km": round(alt_distance, 1),
            "duration_hours": round(alt_duration, 1),
            "fuel_cost_pkr": int(alt_fuel_cost),
            "toll_cost_pkr": int(alt_toll_cost),
            "total_cost_pkr": int(alt_total_cost),
            "co2_emissions_kg": round(alt_co2, 2),
            "route_type": "alternative",
            "description": "Slightly longer but potentially less traffic"
        })
        
        # Scenic route (longer, avoids motorways)
        scenic_distance = distance_km * 1.25
        scenic_duration = duration_hours * 1.4
        scenic_fuel_needed = scenic_distance / vehicle_spec['kmpl']
        scenic_fuel_cost = scenic_fuel_needed * fuel_price
        scenic_toll_cost = toll_cost * 0.3  # 70% cheaper tolls
        scenic_total_cost = scenic_fuel_cost + scenic_toll_cost
        scenic_co2 = scenic_fuel_needed * self.co2_factor
        
        options.append({
            "name": f"{origin} → {destination} (Scenic)",
            "distance_km": round(scenic_distance, 1),
            "duration_hours": round(scenic_duration, 1),
            "fuel_cost_pkr": int(scenic_fuel_cost),
            "toll_cost_pkr": int(scenic_toll_cost),
            "total_cost_pkr": int(scenic_total_cost),
            "co2_emissions_kg": round(scenic_co2, 2),
            "route_type": "scenic",
            "description": "Avoids motorways, more scenic but longer"
        })
        
        return options