# config.py

# --- URL and Site Configuration ---
BASE_URL = "https://www.bestbuy.com"
CATEGORY = "Laptops"

# --- Filter Parameters ---
# The script will loop through each of these brands one by one.
FILTER_BRANDS = ["HP", "Dell", "Apple"] 
FILTER_PRICE_MIN = "500"
FILTER_PRICE_MAX = "1500"
FILTER_RATING_ID = "customer-rating-4_&_Up" 

# --- File Paths ---
LOGS_DIR = "project/logs"
DATA_DIR = "project/data"
REPORTS_DIR = "project/reports" 
SCREENSHOT_PATH = f"{LOGS_DIR}/error_screenshot.png"
# Success screenshots are now saved per brand in the apply_filters function

# --- WebDriver Settings ---
# Set to False to see the browser in action for debugging
HEADLESS_MODE = True