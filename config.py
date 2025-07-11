# config.py

# --- URL and Site Configuration ---
BASE_URL = "https://www.bestbuy.com"
CATEGORY = "Laptops"

# --- Filter Parameters [cite: BlueOceanSP - Web-Automation-Case-Study (1).md] ---
# The script will loop through each of these brands one by one.
FILTER_BRANDS = ["HP", "Dell", "Apple"] 
FILTER_PRICE_MIN = "500"
FILTER_PRICE_MAX = "1500"
FILTER_RATING_ID = "customer-rating-4_&_Up" 

# --- File Paths ---
LOGS_DIR = "logs"
DATA_DIR = "data"
REPORTS_DIR = "reports"
# Consolidated output file path
OUTPUT_FILE_PATH = f"{DATA_DIR}/all_laptops.json"

# --- Caching Settings ---
CACHE_ENABLED = True
CACHE_EXPIRATION_HOURS = 24 # Cache is valid for 24 hours
CACHE_DIR = f"{DATA_DIR}/cache"

# --- WebDriver Settings ---
# Set to False to see the browser in action for debugging
HEADLESS_MODE = True
