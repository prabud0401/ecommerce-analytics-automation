# project/tests/test_main.py

import unittest
from unittest.mock import patch
import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main

class TestMain(unittest.TestCase):

    @patch('main.webdriver.Chrome')
    def test_initialize_driver(self, mock_chrome):
        """
        Test that the initialize_driver function attempts to create a Chrome driver.
        This is a basic test to ensure the function can be called without crashing.
        """
        # We patch webdriver.Chrome to avoid actually launching a browser
        driver_instance = main.initialize_driver()
        
        # Assert that the Chrome class was instantiated
        self.assertTrue(mock_chrome.called)
        # Assert that the function returns the mocked driver instance
        self.assertEqual(driver_instance, mock_chrome.return_value)

if __name__ == '__main__':
    unittest.main()
