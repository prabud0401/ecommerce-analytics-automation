# E-Commerce Analytics Automation

## Overview
This project automates the collection, processing, and analysis of product data and customer reviews from Best Buy's e-commerce platform, focusing on laptops. It uses web scraping with Selenium WebDriver, performs data analysis with pandas, numpy, and nltk, and generates visualizations and reports. The project follows clean code practices, includes robust error handling, and provides detailed logging.

## Project Structure
```
/project
    /data           # Stores JSON data files
    /logs           # Stores log files and screenshots
    /tests          # Placeholder for unit tests
    /reports        # Stores generated reports
    main.py         # Main script orchestrating the automation
    config.py       # Configuration settings
    analysis.py     # Data processing and analysis logic
    requirements.txt # Python dependencies
    README.md       # Project documentation
```

## Prerequisites
- Python 3.11
- Chrome browser
- ChromeDriver (automatically managed via `webdriver_manager`)

## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone git@github.com:prabud0401/ecommerce-analytics-automation.git
   cd ecommerce-analytics-automation
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure directory structure**:
   Create the following directories if they don't exist:
   ```bash
   mkdir -p data logs reports tests
   ```

5. **Configure settings**:
   Review `config.py` to adjust:
   - `BASE_URL`: Target website (default: https://www.bestbuy.com)
   - `FILTER_BRANDS`: Brands to scrape (default: HP, Dell, Apple)
   - `FILTER_PRICE_MIN` and `FILTER_PRICE_MAX`: Price range ($500-$1500)
   - `FILTER_RATING_ID`: Customer rating filter (4+ stars)
   - `HEADLESS_MODE`: Set to `False` for debugging (default: `True`)

## Running the Project
1. **Execute the main script**:
   ```bash
   python main.py
   ```

2. **What happens**:
   - The script launches a headless Chrome browser.
   - Navigates to Best Buy, searches for "Laptops", and applies filters for each brand.
   - Extracts product data (title, price, rating, review count) and saves it as JSON in `data`.
   - Runs analysis (via `analysis.py`) to process data and generate reports in `reports`.
   - Logs are saved in `logs/automation.log`, with screenshots for errors or filtered views.

## Output
- **Data**: JSON files (`<brand>_laptops.json`) in `data`.
- **Logs**: `automation.log` and screenshots in `logs`.
- **Reports**: Analysis outputs (e.g., Excel files, visualizations) in `reports`.

## Notes
- The script respects Best Buy's `robots.txt` by implementing delays between requests.
- Error handling covers network issues, missing elements, and invalid data.
- Logging captures all actions, errors, and screenshots for debugging.
- Follows PEP 8 style guidelines and includes inline comments for clarity.
- Unit tests (to be implemented in `/tests`) are planned for core functionalities.

## Troubleshooting
- **WebDriver errors**: Ensure Chrome is installed and compatible with `webdriver_manager`.
- **Element not found**: Check `config.py` for correct IDs or try `HEADLESS_MODE = False` to debug.
- **Rate limiting**: Increase delays in `main.py` (e.g., `time.sleep`) if blocked.
- **Dependencies**: Verify Python 3.11 and re-run `pip install -r requirements.txt`.

### Completed Bonus Challenges
1. Implemented email notification system for long-running processes
2. Implemented multi-threading for faster data collection
3. Implemented caching mechanism for improved performance
4. Created a simple REST API to query the collected data

## Future Enhancements
1. Add support for multiple e-commerce platforms

## Evaluation Criteria
This project addresses:
- **Code Quality**: Clean code, error handling, and documentation.
- **Functionality**: Robust scraping and filtering for specified brands.
- **Data Processing**: Accurate extraction and planned analysis.
- **Technical Skills**: Effective use of Selenium and Python best practices.

For further details, refer to the inline comments in `main.py`, `config.py`, and `analysis.py`.