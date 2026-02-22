import scrapy

class FreightListingItem(scrapy.Item):
    source = scrapy.Field()
    origin_city = scrapy.Field()
    destination_city = scrapy.Field()
    vehicle_type = scrapy.Field()
    load_weight = scrapy.Field()
    price_pkr = scrapy.Field()
    phone_hash = scrapy.Field()
    scraped_at = scrapy.Field()
    raw_data = scrapy.Field()
    
    # Additional fields for processing
    vehicle_category = scrapy.Field()  # 1-4
    is_valid = scrapy.Field()  # Boolean