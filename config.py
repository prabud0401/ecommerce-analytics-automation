# config.py

# --- URL and Site Configuration ---
BASE_URL = "https://www.bestbuy.com"
CATEGORY = "Laptops"

# --- Filter Parameters [cite: BlueOceanSP - Web-Automation-Case-Study (1).md] ---
FILTER_BRANDS = ["HP", "Dell", "Apple"] 
FILTER_PRICE_MIN = "500"
FILTER_PRICE_MAX = "1500"
FILTER_RATING_ID = "customer-rating-4_&_Up" 

# --- File Paths ---
LOGS_DIR = "logs"
DATA_DIR = "data"
REPORTS_DIR = "reports"
OUTPUT_FILE_PATH = f"{DATA_DIR}/all_laptops.json"

# --- Caching Settings ---
CACHE_ENABLED = True
CACHE_EXPIRATION_HOURS = 24 # Cache is valid for 24 hours
CACHE_DIR = f"{DATA_DIR}/cache"

# --- Email Settings ---
EMAIL_NOTIFICATIONS_ENABLED = True
SMTP_SERVER = "smtp.gmail.com"  # Example for Gmail
SMTP_PORT = 587
# IMPORTANT: Use an App Password for security, not your regular email password.
EMAIL_SENDER = "prabud0401@gmail.com"
EMAIL_PASSWORD = "nsdq eiej vcoy ttlz" 
EMAIL_RECIPIENT = "prabud0401@gmail.com"

# --- WebDriver Settings ---
HEADLESS_MODE = True
