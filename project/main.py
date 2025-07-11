# main.py

import logging
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import config
import analysis 

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{config.LOGS_DIR}/automation.log"),
        logging.StreamHandler()
    ]
)

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

def extract_product_data(driver, brand, all_products_list):
    """Extracts data and appends it to a master list."""
    logging.info(f"Extracting data for {brand}.")
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
        all_products_list.append(product_info)
        logging.info(f"Extracted: {title} | Rating: {rating} | Reviews: {review_count}")

def main():
    """Main function to orchestrate the automation for each brand."""
    all_products = []
    driver = initialize_driver()

    if driver:
        try:
            # --- Scraping Phase ---
            # Navigate to the initial search page once
            if not navigate_and_search(driver):
                logging.error("Failed to navigate to initial search page. Aborting.")
                return

            for brand in config.FILTER_BRANDS:
                logging.info(f"--- Starting scraping process for brand: {brand} ---")
                
                # Apply filters for the current brand
                if apply_filters(driver, brand):
                    extract_product_data(driver, brand, all_products)
                else:
                    logging.error(f"Could not apply filters for brand {brand}. Skipping.")
                
                # Go back to the unfiltered search results page for the next brand
                logging.info(f"Resetting for next brand...")
                driver.get("https://www.bestbuy.com/site/searchpage.jsp?st=Laptops")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-list-item")))

        finally:
            logging.info("--- Finished all scraping. Closing WebDriver. ---")
            driver.quit()
    
    # --- Save Consolidated Data ---
    if all_products:
        with open(config.OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(all_products, f, indent=4)
        logging.info(f"Successfully saved a total of {len(all_products)} products to {config.OUTPUT_FILE_PATH}")
    else:
        logging.warning("No products were scraped. Skipping data save.")

    # --- Analysis Phase ---
    analysis.run_analysis()


if __name__ == "__main__":
    main()
