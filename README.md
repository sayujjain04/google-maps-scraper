# Google Maps Scraper

This Python script leverages Selenium and BeautifulSoup to scrape business data from Google Maps based on user-defined parameters like business type, search distance, and geographic coordinates. It supports recursive searches to refine and expand data collection while avoiding duplicates.

---

## Features

1. **Headless WebDriver Initialization**  
   Utilizes Selenium's Firefox WebDriver with optional headless mode for efficient, non-UI scraping.

2. **Dynamic Search URL Construction**  
   Generates Google Maps search URLs based on business type, distance, and location.

3. **Automated Cookie Consent Handling**  
   Dismisses Google's cookie consent prompt for uninterrupted automation.

4. **Detailed Business Information Extraction**  
   Retrieves comprehensive business details such as:
   - Name
   - Rating
   - Reviews
   - Services offered
   - Address
   - Phone number
   - Website URL
   - All user reviews

5. **Recursive Search for Broader Data**  
   Dynamically reduces search areas to find additional businesses within smaller regions.

6. **JSON Output with Deduplication**  
   Saves data into a JSON file, ensuring no duplicate entries.

---

## Installation and Requirements

- **Python 3.7+**
- **Dependencies**: Install the required libraries using:
  ```bash
  pip install selenium beautifulsoup4
  ```
- **GeckoDriver**: Ensure GeckoDriver is installed and added to your system's PATH for Firefox WebDriver.

---

## Usage

### 1. Input Parameters
Modify the parameters in the `main()` function to set up your scraping session:
- `business_type`: The type of business to search (e.g., "factories").
- `initial_distance`: Search radius in kilometers.
- `latitude` and `longitude`: Geographic coordinates for the search center.
- `json_filepath`: Path to save the scraped data as a JSON file.

### 2. Running the Script
Execute the script:
```bash
python google_maps_scraper.py
```

### 3. Output
- Data is saved to the specified JSON file.
- Logs are displayed in the console for real-time updates.

---

## Functions

### `initialize_webdriver(headless=True)`
Initializes and configures the Firefox WebDriver.

### `build_search_url(business_type, distance, latitude, longitude, unit='km')`
Constructs a Google Maps search URL.

### `dismiss_cookie_consent(driver)`
Handles cookie consent pop-ups automatically.

### `extract_business_details(driver, index)`
Scrapes detailed business information from a specific listing.

### `scrape_reviews(driver)`
Extracts all reviews from the reviews section.

### `save_to_json(data, filepath)`
Saves scraped data to a JSON file, avoiding duplicate entries.

### `recursive_search(...)`
Performs recursive searches by refining the geographic area.

---

## Example Use Case

To scrape factories within a 5 km radius of Chicago's coordinates (41.8781, -87.6298):
1. Update `business_type = "factories"` and set `latitude` and `longitude` accordingly.
2. Run the script. The results will be saved to `GoogleMapsData.json`.

---

## Notes
- **Geographic Precision**: Adjust the recursion distance for finer or broader searches.
- **Headless Mode**: Use `headless=True` in `initialize_webdriver()` for faster execution without opening a browser.
- **Legal Considerations**: Ensure compliance with Google’s terms of service.

---

## License
This project is open-source and available under the MIT License.