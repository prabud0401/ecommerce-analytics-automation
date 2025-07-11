import unittest
from unittest.mock import MagicMock, patch
import logging
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import main
import config

class TestEcommerceAutomation(unittest.TestCase):
    def setUp(self):
        """Set up logging and mock WebDriver for each test."""
        logging.basicConfig(level=logging.INFO)
        self.driver = MagicMock()
        self.mock_wait = MagicMock(spec=WebDriverWait)
        self.mock_ec = MagicMock(spec=EC)

    @patch('main.webdriver.Chrome')
    @patch('main.ChromeDriverManager')
    def test_initialize_driver_success(self, mock_driver_manager, mock_chrome):
        """Test WebDriver initialization in headless mode."""
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"

        driver = main.initialize_driver()
        
        self.assertIsNotNone(driver)
        mock_chrome.assert_called_once()
        mock_driver_manager.return_value.install.assert_called_once()
        self.assertTrue(mock_chrome.call_args[1]['options'].add_argument.called_with('--headless'))

    @patch('main.webdriver.Chrome')
    def test_initialize_driver_failure(self, mock_chrome):
        """Test WebDriver initialization failure handling."""
        mock_chrome.side_effect = WebDriverException("Driver not found")
        
        driver = main.initialize_driver()
        
        self.assertIsNone(driver)

    @patch('main.WebDriverWait')
    def test_navigate_and_search_success(self, mock_wait):
        """Test successful navigation and search."""
        self.driver.get = MagicMock()
        self.driver.find_element = MagicMock()
        mock_search_bar = MagicMock()
        mock_search_button = MagicMock()
        mock_wait.return_value.until.side_effect = [
            MagicMock(),  # Country selection link
            mock_search_bar,  # Search bar
            MagicMock()  # Product list
        ]
        self.driver.find_element.side_effect = [mock_search_button]

        result = main.navigate_and_search(self.driver)
        
        self.assertTrue(result)
        self.driver.get.assert_called_with(config.BASE_URL)
        mock_search_bar.clear.assert_called_once()
        mock_search_bar.send_keys.assert_called_with(config.CATEGORY)
        mock_search_button.click.assert_called_once()

    @patch('main.WebDriverWait')
    def test_navigate_and_search_no_country_selection(self, mock_wait):
        """Test navigation when country selection page is not present."""
        self.driver.get = MagicMock()
        self.driver.find_element = MagicMock()
        mock_search_bar = MagicMock()
        mock_search_button = MagicMock()
        mock_wait.return_value.until.side_effect = [
            TimeoutException("No country selection"),  # Country selection fails
            mock_search_bar,  # Search bar
            MagicMock()  # Product list
        ]
        self.driver.find_element.side_effect = [mock_search_button]

        result = main.navigate_and_search(self.driver)
        
        self.assertTrue(result)
        self.driver.get.assert_called_with(config.BASE_URL)
        mock_search_bar.clear.assert_called_once()

    @patch('main.WebDriverWait')
    def test_navigate_and_search_failure(self, mock_wait):
        """Test navigation failure handling."""
        self.driver.get = MagicMock(side_effect=WebDriverException("Network error"))
        self.driver.save_screenshot = MagicMock()
        
        result = main.navigate_and_search(self.driver)
        
        self.assertFalse(result)
        self.driver.save_screenshot.assert_called_with(config.SCREENSHOT_PATH)

    @patch('main.WebDriverWait')
    def test_apply_filters_success(self, mock_wait):
        """Test successful application of brand and rating filters."""
        mock_product_list = MagicMock()
        mock_brand_checkbox = MagicMock()
        mock_rating_checkbox = MagicMock()
        mock_wait.return_value.until.side_effect = [
            mock_product_list,  # Product list for brand
            mock_brand_checkbox,  # Brand checkbox
            mock_product_list,  # Product list after brand filter
            mock_rating_checkbox  # Rating checkbox
        ]
        self.driver.execute_script = MagicMock()
        self.driver.save_screenshot = MagicMock()
        
        result = main.apply_filters(self.driver, "HP")
        
        self.assertTrue(result)
        mock_brand_checkbox.click.assert_called_once()
        mock_rating_checkbox.click.assert_called_once()
        self.driver.save_screenshot.assert_called_with(f"{config.LOGS_DIR}/filtered_view_HP.png")

    @patch('main.WebDriverWait')
    def test_apply_filters_failure(self, mock_wait):
        """Test failure in applying filters."""
        mock_wait.return_value.until.side MacquarieMagicMock(side_effect=TimeoutException("Element not found"))
        self.driver.save_screenshot = MagicMock()
        
        result = main.apply_filters(self.driver, "HP")
        
        self.assertFalse(result)
        self.driver.save_screenshot.assert_called_with(config.SCREENSHOT_PATH)

    @patch('main.WebDriverWait')
    def test_extract_product_data(self, mock_wait):
        """Test product data extraction and JSON storage."""
        mock_card = MagicMock()
        mock_title = MagicMock()
        mock_title.text = "HP Laptop"
        mock_price = MagicMock()
        mock_price.text = "$999.99"
        mock_review_p = MagicMock()
        mock_review_p.get_attribute.return_value = "Rating 4.5 out of 5 stars"
        mock_review_count = MagicMock()
        mock_review_count.text = "(100)"
        
        mock_card.find_elements = MagicMock(return_value=[mock_card])
        mock_card.find_element.side_effect = [mock_price, mock_review_count]
        self.driver.find_elements.return_value = [mock_card]
        mock_wait.return_value.until.side_effect = [mock_title, mock_review_p]
        self.driver.execute_script = MagicMock()
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            main.extract_product_data(self.driver, "HP")
            
            mock_file.assert_called_with(f"{config.DATA_DIR}/hp_laptops.json", "w", encoding="utf-8")
            mock_file().write.assert_called()
            written_data = json.loads(mock_file().write.call_args[0][0])
            self.assertEqual(len(written_data), 1)
            self.assertEqual(written_data[0]["title"], "HP Laptop")
            self.assertEqual(written_data[0]["price"], "$999.99")
            self.assertEqual(written_data[0]["rating"], "4.5")
            self.assertEqual(written_data[0]["review_count"], "100")

if __name__ == '__main__':
    unittest.main()