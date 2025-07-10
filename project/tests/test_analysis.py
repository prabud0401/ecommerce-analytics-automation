# project/tests/test_analysis.py

import unittest
from unittest.mock import patch, mock_open
import pandas as pd
import json
import sys
import os

# Add the project directory to the Python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import analysis

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        """Set up a sample DataFrame for testing."""
        self.sample_data = [
            {"brand": "TestBrand", "title": "Laptop 1", "price": "$1,299.99", "rating": "4.5", "review_count": "150"},
            {"brand": "TestBrand", "title": "Laptop 2", "price": "999.00", "rating": "4.8", "review_count": "200"},
            {"brand": "AnotherBrand", "title": "Laptop 3", "price": "$750.50", "rating": "3.9", "review_count": "50"},
            {"brand": "TestBrand", "title": "Laptop 4", "price": "N/A", "rating": "4.1", "review_count": "100"},
        ]
        self.df = pd.DataFrame(self.sample_data)

    @patch('glob.glob')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_all_scraped_data(self, mock_file, mock_glob):
        """Test that JSON files are correctly loaded and combined into a DataFrame."""
        # Mock the file system to return a fake file list and file content
        mock_glob.return_value = ['project/data/fake_data.json']
        mock_file.return_value.read.return_value = json.dumps(self.sample_data)

        df = analysis.load_all_scraped_data()
        
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 4)
        self.assertListEqual(list(df.columns), ['brand', 'title', 'price', 'rating', 'review_count'])
        self.assertEqual(df.iloc[0]['title'], 'Laptop 1')

    def test_clean_data(self):
        """Test the data cleaning and type conversion logic."""
        cleaned_df = analysis.clean_data(self.df.copy())

        # Check that rows with invalid prices are dropped
        self.assertEqual(len(cleaned_df), 3)

        # Check data types
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_df['price']))
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_df['rating']))
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_df['review_count']))

        # Check price cleaning
        self.assertAlmostEqual(cleaned_df.iloc[0]['price'], 1299.99)
        self.assertAlmostEqual(cleaned_df.iloc[1]['price'], 999.00)

    @patch('glob.glob')
    def test_load_all_scraped_data_no_files(self, mock_glob):
        """Test behavior when no data files are found."""
        mock_glob.return_value = [] # No files found
        df = analysis.load_all_scraped_data()
        self.assertIsNone(df)

if __name__ == '__main__':
    unittest.main()
