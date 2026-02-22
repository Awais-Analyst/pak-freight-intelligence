import scrapy
import re
from ..items import FreightListingItem

class OlxFreightSpider(scrapy.Spider):
    name = 'olx_freight'
    allowed_domains = ['olx.com.pk']
    
    # Major city pairs for freight
    start_urls = [
        # Karachi to other cities
        'https://www.olx.com.pk/ads/q-freight-karachi/',
        'https://www.olx.com.pk/ads/q-transportation-karachi/',
        'https://www.olx.com.pk/ads/q-truck-karachi/',
        
        # Lahore to other cities
        'https://www.olx.com.pk/ads/q-freight-lahore/',
        'https://www.olx.com.pk/ads/q-transportation-lahore/',
        'https://www.olx.com.pk/ads/q-truck-lahore/',
        
        # Islamabad/Rawalpindi
        'https://www.olx.com.pk/ads/q-freight-islamabad/',
        'https://www.olx.com.pk/ads/q-freight-rawalpindi/',
        
        # Peshawar
        'https://www.olx.com.pk/ads/q-freight-peshawar/',
        
        # Multan
        'https://www.olx.com.pk/ads/q-freight-multan/',
        
        # Faisalabad
        'https://www.olx.com.pk/ads/q-freight-faisalabad/',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
    }
    
    def parse(self, response):
        # Extract listing URLs
        listing_urls = response.css('a[href*="/item/"]::attr(href)').getall()
        for url in listing_urls:
            yield response.follow(url, self.parse_listing)
        
        # Pagination - be conservative
        next_page = response.css('a[data-aut-id="btnLoadMore"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_listing(self, response):
        item = FreightListingItem()
        item['source'] = 'olx'
        
        # Extract title
        title = response.css('h1[data-aut-id="itemTitle"]::text').get()
        if not title:
            title = response.css('title::text').get()
        
        # Extract price
        price_text = response.css('span[data-aut-id="itemPrice"]::text').get()
        if price_text:
            price_match = re.search(r'[\d,]+', price_text)
            if price_match:
                item['price_pkr'] = int(price_match.group().replace(',', ''))
        
        # Extract description
        description = response.css('div[data-aut-id="itemDescriptionContent"] span::text').get()
        if not description:
            description = ""
        
        # Extract location
        location = response.css('span[data-aut-id="itemLocation"]::text').get()
        
        # Parse origin/destination from title/description
        cities = self.extract_cities(title + " " + description)
        if len(cities) >= 2:
            item['origin_city'] = cities[0]
            item['destination_city'] = cities[1]
        elif location:
            # Try to use location as one city
            item['origin_city'] = location
        
        # Extract vehicle type from title/description
        item['vehicle_type'] = self.extract_vehicle_type(title + " " + description)
        
        # Extract load weight
        item['load_weight'] = self.extract_weight(title + " " + description)
        
        # Extract phone if available
        phone_match = re.search(r'03\d{9}', title + " " + description)
        if phone_match:
            item['phone_hash'] = phone_match.group()
        
        yield item
    
    def extract_cities(self, text):
        """Extract city names from text"""
        # Major Pakistani cities
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
        text_lower = text.lower()
        
        for city in cities:
            if city.lower() in text_lower:
                found_cities.append(city)
        
        return found_cities
    
    def extract_vehicle_type(self, text):
        """Extract vehicle type from text"""
        text_lower = text.lower()
        
        # Check for specific vehicle types
        if any(word in text_lower for word in ['mini truck', 'pickup', 'suzuki', 'carry', 'shehzore']):
            return 'Mini-Truck/Pickup'
        elif any(word in text_lower for word in ['bedford', '10 wheeler', '10 wheel', 'lorry']):
            return 'Bedford/10-Wheeler'
        elif any(word in text_lower for word in ['20ft', '20 feet', 'container']):
            return '20-ft Container'
        elif any(word in text_lower for word in ['40ft', '40 feet', 'articulated', 'trailer']):
            return '40-ft Articulated'
        elif 'truck' in text_lower:
            return 'Truck'
        else:
            return 'Not Specified'
    
    def extract_weight(self, text):
        """Extract load weight from text"""
        weight_patterns = [
            r'(\d+)\s*ton',
            r'(\d+)\s*t',
            r'load\s+(\d+)\s*kg',
            r'weight\s+(\d+)\s*kg'
        ]
        
        text_lower = text.lower()
        for pattern in weight_patterns:
            match = re.search(pattern, text_lower)
            if match:
                weight = int(match.group(1))
                # Convert to tons if in kg
                if 'kg' in pattern and weight > 100:
                    weight = weight / 1000
                return f"{weight} ton"
        
        return 'Not Specified'