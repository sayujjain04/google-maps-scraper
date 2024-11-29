# scraper/google_maps_scraper.py

import json
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    MoveTargetOutOfBoundsException,
)
from bs4 import BeautifulSoup


def initialize_webdriver(headless=True):
    """
    Initializes the Selenium WebDriver with Firefox options.

    Args:
        headless (bool): If True, runs the browser in headless mode.

    Returns:
        WebDriver: An instance of Selenium WebDriver.
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    return driver


def format_coordinates(latitude, longitude):
    """
    Formats latitude and longitude with directional indicators without rounding.

    Args:
        latitude (float): Latitude value.
        longitude (float): Longitude value.

    Returns:
        tuple: Formatted latitude and longitude strings with N/S and E/W indicators.
    """
    lat_dir = 'N' if latitude >= 0 else 'S'
    lon_dir = 'E' if longitude >= 0 else 'W'
    formatted_lat = f"{abs(latitude)}° {lat_dir}"
    formatted_lon = f"{abs(longitude)}° {lon_dir}"
    return formatted_lat, formatted_lon


def build_search_url(business_type, distance, latitude, longitude, unit='km'):
    """
    Constructs the Google Maps search URL based on provided parameters.

    Args:
        business_type (str): Type of business to search for (e.g., "factories").
        distance (int): Distance for the search area.
        latitude (float): Latitude of the search center.
        longitude (float): Longitude of the search center.
        unit (str): Unit of distance ('km' or 'm').

    Returns:
        str: Constructed Google Maps search URL.
    """
    lat, lon = format_coordinates(latitude, longitude)
    query = f"{business_type} within {distance} {unit} of {lat}, {lon}"
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/maps/search/{encoded_query}"
    return url


def dismiss_cookie_consent(driver):
    """
    Attempts to dismiss the cookie consent pop-up on Google Maps.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
    """
    try:
        consent_button = driver.find_element(
            By.XPATH,
            "//button[contains(@aria-label, 'Accept all') or contains(text(), 'Accept all')]"
        )
        consent_button.click()
        print("Cookie consent dismissed.")
    except NoSuchElementException:
        print("No cookie consent prompt found.")


def extract_business_details(driver, index):
    """
    Extracts detailed information about a business from Google Maps.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        index (int): Index of the business entry.

    Returns:
        dict: A dictionary containing business details.
    """
    try:
        entries = driver.find_elements(By.CLASS_NAME, "hfpxzc")
        entry = entries[index]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", entry)
        time.sleep(1)
        ActionChains(driver).move_to_element(entry).click(entry).perform()
        time.sleep(2)

        # Extracting details
        name = entry.get_attribute('aria-label') or 'N/A'
        rating = get_element_text(driver, By.CLASS_NAME, 'MW4etd', index) + "/5" if get_element_text(driver, By.CLASS_NAME, 'MW4etd', index) else 'N/A'
        reviews = get_element_text(driver, By.CLASS_NAME, 'UY7F9', index) or 'N/A'
        service = get_element_text(driver, By.CLASS_NAME, 'Ahnjwc', index) or 'N/A'
        website = get_element_attribute(driver, By.CSS_SELECTOR, ".PLbyfe a", 'href') or 'N/A'
        address = get_element_text(driver, By.CSS_SELECTOR, "div.RcCsl:nth-child(3) button:nth-child(2)", 0) or 'N/A'
        phone = get_element_text(driver, By.CSS_SELECTOR, "div.RcCsl:nth-child(5) button:nth-child(2)", 0) or 'N/A'

        # Click reviews button
        try:
            reviews_button = driver.find_element(By.CSS_SELECTOR, "button.hh2c6:nth-child(2)")
            reviews_button.click()
            time.sleep(2)
        except NoSuchElementException:
            print("Reviews button not found.")

        # Extract reviews
        all_reviews = scrape_reviews(driver)

        return {
            'name': name,
            'rating': rating,
            'reviews': reviews,
            'service': service,
            'website': website,
            'address': address,
            'phone': phone,
            'all_reviews': all_reviews
        }

    except (NoSuchElementException, ElementClickInterceptedException, MoveTargetOutOfBoundsException, IndexError) as e:
        print(f"Error extracting details for entry {index}: {e}")
        return {}


def get_element_text(driver, by, selector, index=0):
    """
    Retrieves text from a specified element.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        by (By): The method to locate elements.
        selector (str): The selector string.
        index (int): The index of the element if multiple are found.

    Returns:
        str: Text content of the element or None.
    """
    try:
        elements = driver.find_elements(by, selector)
        return elements[index].text if elements else None
    except IndexError:
        return None


def get_element_attribute(driver, by, selector, attribute, index=0):
    """
    Retrieves an attribute from a specified element.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        by (By): The method to locate elements.
        selector (str): The selector string.
        attribute (str): The attribute to retrieve.
        index (int): The index of the element if multiple are found.

    Returns:
        str: Attribute value of the element or None.
    """
    try:
        elements = driver.find_elements(by, selector)
        return elements[index].get_attribute(attribute) if elements else None
    except IndexError:
        return None


def scrape_reviews(driver):
    """
    Scrapes all available reviews from the reviews section.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.

    Returns:
        list: A list of review texts.
    """
    reviews = []
    seen = set()
    while True:
        try:
            review_elements = driver.find_elements(By.CSS_SELECTOR, "div.MyEned > span.wiI7pd")
            new_reviews = 0
            for elem in review_elements:
                text = elem.text
                if text not in seen:
                    seen.add(text)
                    reviews.append(text)
                    new_reviews += 1
            if new_reviews > 0:
                driver.execute_script("arguments[0].scrollIntoView(true);", review_elements[-1])
                time.sleep(2)
            else:
                print("No more new reviews found.")
                break
        except Exception as e:
            print(f"Error while scraping reviews: {e}")
            break
    return reviews


def scrape_google_maps(driver, url):
    """
    Scrapes business data from Google Maps based on the provided search URL.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        url (str): Google Maps search URL.

    Returns:
        list: A list of dictionaries containing business details.
    """
    driver.get(url)
    time.sleep(3)  # Allow the page to load

    dismiss_cookie_consent(driver)

    # Parse initial page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    titles = soup.find_all(class_="hfpxzc")
    ratings = soup.find_all(class_='MW4etd')
    reviews = soup.find_all(class_='UY7F9')
    services = soup.find_all(class_='Ahnjwc')

    results = []
    for i in range(len(titles)):
        business = extract_business_details(driver, i)
        if business:
            results.append(business)
            print(f"Scraped business: {business['name']}")

    return results


def save_to_json(data, filepath):
    """
    Saves scraped data to a JSON file, avoiding duplicates.

    Args:
        data (list): List of business dictionaries.
        filepath (str): Path to the JSON file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_names = {entry['name'] for entry in existing_data}
    new_entries = [entry for entry in data if entry['name'] not in existing_names]

    if new_entries:
        existing_data.extend(new_entries)
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)
        print(f"Saved {len(new_entries)} new entries to {filepath}")
    else:
        print("No new entries to save.")


def recursive_search(driver, business_type, distance, latitude, longitude, filepath, seen_data, min_results=10, unit='km'):
    """
    Recursively searches Google Maps within specified distances to gather business data.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        business_type (str): Type of business to search for.
        distance (int): Current search distance.
        latitude (float): Latitude of the search center.
        longitude (float): Longitude of the search center.
        filepath (str): Path to the JSON file for saving results.
        seen_data (dict): Dictionary to track seen businesses.
        min_results (int): Minimum number of new results to continue recursion.
        unit (str): Unit of distance ('km' or 'm').
    """
    search_url = build_search_url(business_type, distance, latitude, longitude, unit)
    print(f"Searching: {search_url}")
    scraped_data = scrape_google_maps(driver, search_url)

    # Filter new entries
    new_data = []
    for entry in scraped_data:
        if entry['name'] not in seen_data:
            seen_data[entry['name']] = entry
            new_data.append(entry)

    save_to_json(new_data, filepath)

    if len(new_data) >= min_results:
        print(f"Refining search area for distance {distance} {unit}.")
        if unit == 'km' and distance > 1:
            new_distance = distance // 2
            new_unit = 'km'
        else:
            new_distance = distance * 1000 if unit == 'km' else distance // 2
            new_unit = 'm'

        # Define new search points around the current center
        offsets = [
            (latitude + new_distance / 111.32, longitude),       # North
            (latitude - new_distance / 111.32, longitude),       # South
            (latitude, longitude + new_distance / (111.32 * abs(math.cos(math.radians(latitude))))) if math.cos(math.radians(latitude)) != 0 else longitude,  # East
            (latitude, longitude - new_distance / (111.32 * abs(math.cos(math.radians(latitude))))) if math.cos(math.radians(latitude)) != 0 else longitude,  # West
        ]

        for new_lat, new_lon in offsets:
            recursive_search(
                driver,
                business_type,
                new_distance,
                new_lat,
                new_lon,
                filepath,
                seen_data,
                min_results,
                new_unit
            )


def main():
    import math

    # User inputs
    business_type = "factories"       # Example business type
    initial_distance = 5              # Initial distance
    latitude = 41.8781                 # Example latitude (Chicago)
    longitude = -87.6298               # Example longitude (Chicago)
    json_filepath = 'GoogleMapsData.json'

    # Initialize WebDriver
    driver = initialize_webdriver(headless=False)  # Set headless=True to run without a browser window

    # Dictionary to track seen businesses
    seen_businesses = {}

    try:
        recursive_search(
            driver,
            business_type,
            initial_distance,
            latitude,
            longitude,
            json_filepath,
            seen_businesses
        )
    finally:
        driver.quit()
        print("WebDriver closed.")


if __name__ == "__main__":
    main()
