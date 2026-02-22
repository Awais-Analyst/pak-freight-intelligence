import scrapy
import re
from ..items import FreightListingItem

class PakWheelsFreightSpider(scrapy.Spider):
    name = 'pakwheels_freight'
    allowed_domains = ['pakwheels.com']
    
    start_urls = [
        'https://www.pakwheels.com/used-bikes/',  # Some freight listings appear here
        'https://www.pakwheels.com/trucks/',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
    }
    
    def parse(self, response):
        # Extract listing URLs
        listing_urls = response.css('a[href*="/used-bikes/"]::attr(href)').getall()
        listing_urls += response.css('a[href*="/trucks/"]::attr(href)').getall()
        
        for url in listing_urls:
            if 'freight' in url.lower() or 'transport' in url.lower() or 'load' in url.lower():
                yield response.follow(url, self.parse_listing)
    
    def parse_listing(self, response):
        item = FreightListingItem()
        item['source'] = 'pakwheels'
        
        # Extract title
        title = response.css('h1.ad-detail-title::text').get()
        if not title:
            title = response.css('title::text').get()
        
        # Extract price
        price_text = response.css('div.price-box strong::text').get()
        if price_text:
            price_match = re.search(r'[\d,]+', price_text)
            if price_match:
                item['price_pkr'] = int(price_match.group().replace(',', ''))
        
        # Extract description
        description = response.css('div.detailed-show div.description::text').get()
        if not description:
            description = ""
        
        # Extract location
        location = response.css('div.location::text').get()
        
        # Parse origin/destination
        cities = self.extract_cities(title + " " + description)
        if len(cities) >= 2:
            item['origin_city'] = cities[0]
            item['destination_city'] = cities[1]
        elif location:
            item['origin_city'] = location
        
        # Extract vehicle type
        item['vehicle_type'] = self.extract_vehicle_type(title + " " + description)
        
        # Extract load weight
        item['load_weight'] = self.extract_weight(title + " " + description)
        
        # Extract phone
        phone_match = re.search(r'03\d{9}', title + " " + description)
        if phone_match:
            item['phone_hash'] = phone_match.group()
        
        yield item
    
    def extract_cities(self, text):
        """Extract city names from text"""
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
        text_lower = text.lower()
        
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
                if 'kg' in pattern and weight > 100:
                    weight = weight / 1000
                return f"{weight} ton"
        
        return 'Not Specified'