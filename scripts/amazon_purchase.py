"""
Amazon Login and Purchase Automation Script

Automates login, search, product selection, delivery pincode setting, cart addition, and checkout for a specified Amazon product.

Setup:
- Install Python 3.8+
- pip install selenium
- Download ChromeDriver and add to PATH
- Set environment variables:
    AMAZON_USERNAME, AMAZON_PASSWORD, AMAZON_ASIN, AMAZON_PINCODE

Usage:
    python amazon_purchase.py

Troubleshooting:
    - Ensure credentials are correct
    - Update selectors if Amazon UI changes
    - Review logs for errors

Author: Senior Test Automation Engineer
Date: 2024-06
"""

import os
import sys
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
    ElementClickInterceptedException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- CONFIGURATION ----
AMAZON_URL = "https://www.amazon.in/"
ASIN = os.getenv("AMAZON_ASIN", "B088N8G9RL")
PINCODE = os.getenv("AMAZON_PINCODE", "560001")
USERNAME = os.getenv("AMAZON_USERNAME")
PASSWORD = os.getenv("AMAZON_PASSWORD")
LOG_FILE = "amazon_purchase.log"

# ---- LOGGING SETUP ----
logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def validate_env():
    missing = []
    if not USERNAME:
        missing.append("AMAZON_USERNAME")
    if not PASSWORD:
        missing.append("AMAZON_PASSWORD")
    if missing:
        logging.error(f"Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

def get_product_url(asin):
    return f"{AMAZON_URL}dp/{asin}"

def wait_and_find(driver, by, value, timeout=15):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        logging.error(f"Element not found: {value}")
        raise

def login_amazon(driver):
    logging.info("Navigating to Amazon login page...")
    driver.get(AMAZON_URL)
    time.sleep(2)
    try:
        sign_in_btn = wait_and_find(driver, By.ID, "nav-link-accountList")
        sign_in_btn.click()
        email_field = wait_and_find(driver, By.ID, "ap_email")
        email_field.send_keys(USERNAME)
        driver.find_element(By.ID, "continue").click()
        password_field = wait_and_find(driver, By.ID, "ap_password")
        password_field.send_keys(PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()
        time.sleep(3)
        # Check for CAPTCHA
        if "authentication required" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
            logging.error("CAPTCHA detected. Manual intervention required.")
            sys.exit(1)
        logging.info("Login successful.")
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Login failed: {e}")
        sys.exit(1)

def set_delivery_pincode(driver, pincode):
    logging.info(f"Setting delivery pincode: {pincode}")
    try:
        # On product page, set pincode
        pincode_btn = wait_and_find(driver, By.ID, "contextualIngressPtLabel_deliveryShortLine", timeout=10)
        pincode_btn.click()
        time.sleep(1)
        pincode_input = wait_and_find(driver, By.ID, "GLUXZipUpdateInput", timeout=10)
        pincode_input.clear()
        pincode_input.send_keys(pincode)
        driver.find_element(By.ID, "GLUXZipUpdate").click()
        time.sleep(2)
        logging.info("Pincode set successfully.")
    except Exception as e:
        logging.warning(f"Pincode setting failed or not needed: {e}")

def add_to_cart(driver):
    logging.info("Adding product to cart...")
    try:
        add_cart_btn = wait_and_find(driver, By.ID, "add-to-cart-button", timeout=10)
        add_cart_btn.click()
        time.sleep(2)
        # Handle popup for protection plans, etc.
        try:
            no_thanks_btn = driver.find_element(By.XPATH, "//input[@aria-labelledby='attachSiNoCoverage-announce']")
            no_thanks_btn.click()
            time.sleep(1)
        except NoSuchElementException:
            pass
        logging.info("Product added to cart.")
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Add to cart failed: {e}")
        sys.exit(1)

def proceed_to_checkout(driver):
    logging.info("Proceeding to checkout...")
    try:
        proceed_btn = wait_and_find(driver, By.ID, "hlb-ptc-btn-native", timeout=10)
        proceed_btn.click()
        time.sleep(2)
        logging.info("Checkout page loaded. Further steps (address/payment) require manual completion or extension.")
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Proceed to checkout failed: {e}")
        sys.exit(1)

def main():
    validate_env()
    options = Options()
    # Uncomment for headless execution
    # options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1200,800")
    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as e:
        logging.error(f"ChromeDriver initialization failed: {e}")
        sys.exit(1)
    try:
        login_amazon(driver)
        product_url = get_product_url(ASIN)
        logging.info(f"Navigating to product page: {product_url}")
        driver.get(product_url)
        time.sleep(2)
        set_delivery_pincode(driver, PINCODE)
        add_to_cart(driver)
        proceed_to_checkout(driver)
        logging.info("Amazon purchase automation completed successfully.")
    except Exception as e:
        logging.error(f"Automation failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
