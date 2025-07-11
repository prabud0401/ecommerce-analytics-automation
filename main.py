# main.py

import logging
import time
import json
import re
import os
from datetime import datetime, timedelta
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import config
import analysis 
import notifications # Import the new notifications module

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{config.LOGS_DIR}/automation.log"),
        logging.StreamHandler()
    ]
)

def is_cache_valid(cache_path):
    """Checks if a cache file exists and is not expired."""
    if not config.CACHE_ENABLED or not os.path.exists(cache_path):
        return False
    
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
    if datetime.now() - file_mod_time > timedelta(hours=config.CACHE_EXPIRATION_HOURS):
        logging.info(f"Cache file {cache_path} has expired.")
        return False
    
    logging.info(f"Valid cache found for {cache_path}.")
    return True

def initialize_driver():
    """Initializes and returns a Selenium WebDriver instance."""
    chrome_options = Options()
    if config.HEADLESS_MODE:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        logging.info("WebDriver initialized successfully.")
        return driver
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {e}")
        return None

def navigate_and_search(driver):
    """Navigates to the base URL, handles country selection, and searches for Laptops."""
    try:
        driver.get(config.BASE_URL)
        logging.info(f"Successfully navigated to {config.BASE_URL}")
        
        try:
            us_link_xpath = "//a[.//img[@alt='United States']]"
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, us_link_xpath))).click()
            logging.info("Handled country selection by choosing United States.")
        except Exception:
            logging.info("Country selection page did not appear, continuing.")
        
        search_bar = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "autocomplete-search-bar")))
        search_bar.clear()
        search_bar.send_keys(config.CATEGORY)
        driver.find_element(By.ID, "autocomplete-search-button").click()
        logging.info(f"Searched for category: {config.CATEGORY}")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-list-item")))
        logging.info("Product listings page loaded successfully.")
        return True
    except Exception as e:
        logging.error(f"Error in navigation/search: {e}")
        return False

def apply_filters(driver, brand_to_filter):
    """Applies filters for a single brand, price, and rating."""
    try:
        logging.info(f"Applying filters for brand: {brand_to_filter}")
        
        # Apply Brand Filter
        product_list_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "plp-product-list")))
        brand_checkbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, brand_to_filter)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", brand_checkbox)
        time.sleep(1) 
        brand_checkbox.click()
        logging.info(f"Applied brand filter: {brand_to_filter}")
        WebDriverWait(driver, 15).until(EC.staleness_of(product_list_container))
        logging.info(f"Page refreshed after filtering for {brand_to_filter}.")

        # Apply Customer Rating Filter
        product_list_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "plp-product-list")))
        rating_checkbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, config.FILTER_RATING_ID)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", rating_checkbox)
        time.sleep(1)
        rating_checkbox.click()
        logging.info(f"Applied rating filter: {config.FILTER_RATING_ID}")
        WebDriverWait(driver, 15).until(EC.staleness_of(product_list_container))
        logging.info("Page refreshed after rating filter.")

        logging.info("All filters applied successfully for this brand.")
        return True
    except Exception as e:
        logging.error(f"Error applying filters for {brand_to_filter}: {e}")
        return False

def extract_product_data_for_thread(driver, brand):
    """Extracts data for a brand and returns it as a list."""
    logging.info(f"Extracting data for {brand}.")
    products = []
    time.sleep(2)
    
    product_cards = driver.find_elements(By.CLASS_NAME, "product-list-item")
    logging.info(f"Found {len(product_cards)} potential product cards for {brand}.")

    for card in product_cards:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        time.sleep(0.5)

        try:
            title_element = WebDriverWait(card, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "product-title")))
            title = title_element.text.strip()
        except Exception:
            logging.warning("Card skipped because title was not found in time.")
            continue
        
        try:
            price = card.find_element(By.CSS_SELECTOR, "div.customer-price").text.strip()
        except:
            price = "N/A"
            
        try:
            review_p_tag = WebDriverWait(card, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.visually-hidden")))
            review_text = review_p_tag.get_attribute('innerHTML')
            rating_match = re.search(r"Rating ([\d\.]+) out of 5 stars", review_text)
            rating = rating_match.group(1) if rating_match else "N/A"
        except:
            rating = "N/A"

        try:
            review_count_span = card.find_element(By.CSS_SELECTOR, "span.c-reviews")
            review_count = review_count_span.text.strip().replace('(', '').replace(')', '').replace(',', '')
        except:
            review_count = "N/A"

        product_info = {
            "brand": brand,
            "title": title,
            "price": price,
            "rating": rating,
            "review_count": review_count
        }
        products.append(product_info)
    
    return products

def scrape_brand_data(brand):
    """
    A complete scraping pipeline for a single brand, designed to be run in a thread.
    Initializes a driver, scrapes data, and closes the driver.
    """
    logging.info(f"Thread for brand '{brand}' started.")
    driver = initialize_driver()
    if not driver:
        return []

    brand_products = []
    try:
        if navigate_and_search(driver):
            if apply_filters(driver, brand):
                brand_products = extract_product_data_for_thread(driver, brand)
                # Save to cache on successful scrape
                cache_path = os.path.join(config.CACHE_DIR, f"cache_{brand.lower()}.json")
                with open(cache_path, 'w') as f:
                    json.dump(brand_products, f, indent=4)
                logging.info(f"Saved data for '{brand}' to cache.")
    except Exception as e:
        logging.error(f"An error occurred in the thread for brand '{brand}': {e}")
    finally:
        if driver:
            driver.quit()
        logging.info(f"Thread for brand '{brand}' finished and WebDriver closed.")
    
    return brand_products

def main():
    """Main function to orchestrate the automation using caching and a thread pool."""
    start_time = time.time()
    all_products = []
    brands_to_scrape = []

    # Create cache directory if it doesn't exist
    if not os.path.exists(config.CACHE_DIR):
        os.makedirs(config.CACHE_DIR)

    # --- Caching Check ---
    for brand in config.FILTER_BRANDS:
        cache_path = os.path.join(config.CACHE_DIR, f"cache_{brand.lower()}.json")
        if is_cache_valid(cache_path):
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
                all_products.extend(cached_data)
                logging.info(f"Loaded {len(cached_data)} products for '{brand}' from cache.")
        else:
            brands_to_scrape.append(brand)

    # --- Scraping Phase (only for non-cached brands) ---
    if brands_to_scrape:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(brands_to_scrape)) as executor:
            future_to_brand = {executor.submit(scrape_brand_data, brand): brand for brand in brands_to_scrape}
            
            for future in concurrent.futures.as_completed(future_to_brand):
                brand = future_to_brand[future]
                try:
                    data = future.result()
                    if data:
                        all_products.extend(data)
                        logging.info(f"Successfully collected {len(data)} products for brand '{brand}'.")
                except Exception as exc:
                    logging.error(f"Brand '{brand}' generated an exception: {exc}")

    # --- Save Consolidated Data ---
    if all_products:
        with open(config.OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(all_products, f, indent=4)
        logging.info(f"Successfully saved a total of {len(all_products)} products to {config.OUTPUT_FILE_PATH}")
    else:
        logging.warning("No products were scraped or found in cache.")

    # --- Analysis Phase ---
    analysis.run_analysis()

    # --- Email Notification ---
    end_time = time.time()
    duration = end_time - start_time
    email_subject = "E-Commerce Scraping and Analysis Complete"
    email_body = (
        f"The automation script has finished.\n\n"
        f"Total products processed: {len(all_products)}\n"
        f"Total execution time: {duration:.2f} seconds.\n\n"
        f"Reports have been generated in the '{config.REPORTS_DIR}' directory."
    )
    notifications.send_notification_email(email_subject, email_body)


if __name__ == "__main__":
    main()
