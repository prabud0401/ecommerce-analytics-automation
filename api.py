# api.py

import os
import json
import logging
from flask import Flask, request, jsonify
import pandas as pd
import config

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data():
    """Loads the laptop data from the JSON file."""
    if not os.path.exists(config.OUTPUT_FILE_PATH):
        logging.error(f"Data file not found at: {config.OUTPUT_FILE_PATH}")
        return None
    
    # Use pandas for easier filtering and manipulation
    df = pd.read_json(config.OUTPUT_FILE_PATH)
    
    # Convert columns to numeric, coercing errors
    df['price'] = df['price'].replace({r'\$': '', r',': ''}, regex=True)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce')
    
    return df

@app.route('/', methods=['GET'])
def index():
    """Provides basic instructions for using the API."""
    return jsonify({
        "message": "Welcome to the Laptop Data API!",
        "endpoints": {
            "/api/laptops": "Get all laptop data. Supports filtering.",
        },
        "filters": {
            "brand": "Filter by brand (e.g., ?brand=Apple)",
            "min_price": "Filter by minimum price (e.g., ?min_price=1000)",
            "max_price": "Filter by maximum price (e.g., ?max_price=1500)",
            "min_rating": "Filter by minimum rating (e.g., ?min_rating=4.5)"
        }
    })

@app.route('/api/laptops', methods=['GET'])
def get_laptops():
    """Returns laptop data, with optional filtering."""
    df = load_data()
    if df is None:
        return jsonify({"error": "Data not available. Please run the scraping script first."}), 500

    # --- Apply Filters based on Query Parameters ---
    brand = request.args.get('brand')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)

    if brand:
        df = df[df['brand'].str.lower() == brand.lower()]
    
    if min_price:
        df = df[df['price'] >= min_price]

    if max_price:
        df = df[df['price'] <= max_price]
        
    if min_rating:
        df = df[df['rating'] >= min_rating]

    result = df.to_dict(orient='records')
    return jsonify(result)

if __name__ == '__main__':
    # Runs the Flask app on a local development server
    # Accessible at http://127.0.0.1:5000
    app.run(debug=True, port=5000)
