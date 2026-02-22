BOT_NAME = 'freight_scrapers'

SPIDER_MODULES = ['freight_scrapers.spiders']
NEWSPIDER_MODULE = 'freight_scrapers.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure user agent
USER_AGENT = 'FreightBot/1.0 (+https://github.com/yourusername/pak-freight-intelligence)'

# Configure delays
DOWNLOAD_DELAY = 5  # 5 seconds between requests
RANDOMIZE_DOWNLOAD_DELAY = True

# Configure concurrent requests (be polite)
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Disable cookies
COOKIES_ENABLED = False

# Configure pipelines
ITEM_PIPELINES = {
    'freight_scrapers.pipelines.VehicleClassificationPipeline': 100,
    'freight_scrapers.pipelines.DataCleaningPipeline': 200,
    'freight_scrapers.pipelines.SupabasePipeline': 300,
}

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Logging
LOG_LEVEL = 'INFO'

# Auto throttling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Request headers
DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'en',
}