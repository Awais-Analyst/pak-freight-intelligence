import re
import hashlib
import json
from datetime import datetime
from .items import FreightListingItem

class VehicleClassificationPipeline:
    """Classify vehicles into 4 categories based on keywords"""
    
    # Vehicle classification keywords
    VEHICLE_PATTERNS = {
        1: [r'mini', r'pickup', r'suzuki', r'carry', r'loader', r'1[\s-]?ton', r'2[\s-]?ton', r'3[\s-]?ton', 
            r'4[\s-]?ton', r'5[\s-]?ton', r'shehzore', r'hiace'],
        2: [r'bedford', r'10[\s-]?wheeler', r'10[\s-]?wheel', r'8[\s-]?ton', r'10[\s-]?ton', r'12[\s-]?ton', 
            r'14[\s-]?ton', r'lorry', r'truck'],
        3: [r'20[\s-]?ft', r'20[\s-]?feet', r'15[\s-]?ton', r'18[\s-]?ton', r'20[\s-]?ton', r'22[\s-]?ton',
            r'container', r'trailer'],
        4: [r'40[\s-]?ft', r'40[\s-]?feet', r'30[\s-]?ton', r'35[\s-]?ton', r'40[\s-]?ton', r'45[\s-]?ton',
            r'articulated', r'double', r'40ft']
    }
    
    def process_item(self, item, spider):
        vehicle_type = item.get('vehicle_type', '').lower()
        load_weight = item.get('load_weight', '').lower()
        combined_text = f"{vehicle_type} {load_weight}"
        
        # Try to classify
        category = None
        for cat, patterns in self.VEHICLE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    category = cat
                    break
            if category:
                break
        
        item['vehicle_category'] = category
        return item


class DataCleaningPipeline:
    """Clean and validate data"""
    
    PKR_PRICE_RANGE = {
        1: (5000, 150000),    # Mini-Truck
        2: (15000, 300000),   # Bedford
        3: (30000, 500000),   # 20ft
        4: (50000, 800000)    # 40ft
    }
    
    def process_item(self, item, spider):
        # Clean price
        price = item.get('price_pkr')
        if isinstance(price, str):
            price = re.sub(r'[^\d]', '', price)
            try:
                price = int(price)
            except:
                price = None
        item['price_pkr'] = price
        
        # Clean city names
        item['origin_city'] = self.clean_city(item.get('origin_city', ''))
        item['destination_city'] = self.clean_city(item.get('destination_city', ''))
        
        # Hash phone number if present
        phone = item.get('phone_hash')
        if phone and len(phone) > 5:  # Valid phone number
            item['phone_hash'] = hashlib.sha256(phone.encode()).hexdigest()[:16]
        else:
            item['phone_hash'] = None
        
        # Validate
        is_valid = self.validate_item(item)
        item['is_valid'] = is_valid
        
        # Store raw data as JSON
        item['raw_data'] = json.dumps(dict(item), default=str)
        
        return item
    
    def clean_city(self, city):
        if not city:
            return None
        
        city = city.strip()
        # Common city name corrections
        city_corrections = {
            'khi': 'Karachi',
            'lhr': 'Lahore',
            'isb': 'Islamabad',
            'rwp': 'Rawalpindi',
            'pesh': 'Peshawar',
            'psh': 'Peshawar',
            'quetta': 'Quetta',
            'faisalabad': 'Faisalabad',
            'faisal abad': 'Faisalabad',
            'multan': 'Multan',
            'sialkot': 'Sialkot',
            'gujranwala': 'Gujranwala',
            'sargodha': 'Sargodha',
            'bahawalpur': 'Bahawalpur',
            'dg khan': 'Dera Ghazi Khan',
            'dera ghazi': 'Dera Ghazi Khan'
        }
        
        city_lower = city.lower()
        return city_corrections.get(city_lower, city.title())
    
    def validate_item(self, item):
        # Required fields
        if not all([item.get('origin_city'), item.get('destination_city'), item.get('price_pkr')]):
            return False
        
        # Price validation
        price = item.get('price_pkr')
        category = item.get('vehicle_category')
        
        if not price or not category:
            return False
        
        min_price, max_price = self.PKR_PRICE_RANGE.get(category, (0, 1000000))
        if not (min_price <= price <= max_price):
            return False
        
        # Different cities
        if item['origin_city'].lower() == item['destination_city'].lower():
            return False
        
        return True


class SupabasePipeline:
    """Store data in Supabase"""
    
    def __init__(self, supabase_url, supabase_key):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            supabase_url=crawler.settings.get('SUPABASE_URL'),
            supabase_key=crawler.settings.get('SUPABASE_KEY')
        )
    
    def open_spider(self, spider):
        try:
            from supabase import create_client
            self.supabase = create_client(self.supabase_url, self.supabase_key)
        except ImportError:
            spider.logger.error("Supabase client not installed. Install with: pip install supabase")
    
    def process_item(self, item, spider):
        if not item.get('is_valid'):
            spider.logger.debug(f"Skipping invalid item: {item}")
            return item
        
        if not self.supabase:
            return item
        
        try:
            # Insert into raw_listings
            data = {
                'source': item['source'],
                'origin_city': item['origin_city'],
                'destination_city': item['destination_city'],
                'vehicle_type': item['vehicle_type'],
                'load_weight': item['load_weight'],
                'price_pkr': item['price_pkr'],
                'phone_hash': item['phone_hash'],
                'scraped_at': datetime.now().isoformat()
            }
            
            self.supabase.table('raw_listings').insert(data).execute()
            spider.logger.info(f"Stored item: {item['origin_city']} to {item['destination_city']}")
            
        except Exception as e:
            spider.logger.error(f"Error storing item: {e}")
        
        return item