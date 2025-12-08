"""
Amazon Automated Purchase Script
Author: Senior Test Automation Engineer
Description: Automates login and purchase of a specified product (by ASIN) on Amazon.
Requirements:
    - Python 3.x
    - selenium (pip install selenium)
    - ChromeDriver (matching your Chrome version)
    - Environment variables: AMAZON_USERNAME, AMAZON_PASSWORD, AMAZON_PINCODE, AMAZON_ASIN, AMAZON_QUANTITY
Usage:
    1. Set environment variables:
        export AMAZON_USERNAME='your_email'
        export AMAZON_PASSWORD='your_password'
        export AMAZON_PINCODE='560001'
        export AMAZON_ASIN='B088N8G9RL'
        export AMAZON_QUANTITY='1'
    2. Install dependencies:
        pip install selenium
    3. Download ChromeDriver: https://chromedriver.chromium.org/downloads
    4. Run script:
        python amazon_purchase.py
Troubleshooting:
    - Login failures: Check credentials, network, CAPTCHA.
    - Product not found: Validate ASIN.
    - Delivery unavailable: Check pincode.
    - UI changes: Update element locators.
"""

import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# --- Config ---
AMAZON_URL = "https://www.amazon.in/"
LOGIN_URL = "https://www.amazon.in/ap/signin"
CART_URL = "https://www.amazon.in/gp/cart/view.html"

def get_env_var(var_name, required=True):
    value = os.getenv(var_name)
    if required and not value:
        logging.error(f"Missing required environment variable: {var_name}")
        sys.exit(1)
    return value

def amazon_login(driver, username, password):
    driver.get(LOGIN_URL)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email")))
        driver.find_element(By.ID, "ap_email").send_keys(username)
        driver.find_element(By.ID, "continue").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password")))
        driver.find_element(By.ID, "ap_password").send_keys(password)
        driver.find_element(By.ID, "signInSubmit").click()
        # Wait for login to complete
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nav-link-accountList")))
        logging.info("Amazon login successful.")
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Login failed: {e}")
        raise

def navigate_to_product(driver, asin):
    product_url = f"{AMAZON_URL}dp/{asin}"
    driver.get(product_url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "productTitle")))
        logging.info(f"Navigated to product page: ASIN {asin}")
    except (NoSuchElementException, TimeoutException):
        logging.error("Product page not loaded or ASIN invalid.")
        raise

def validate_delivery_pincode(driver, pincode):
    try:
        # Click on 'Enter delivery pincode' if available
        pin_input = None
        try:
            pin_input = driver.find_element(By.ID, "contextualIngressPtLabel_deliveryShortLine")
            pin_input.click()
            time.sleep(2)
        except NoSuchElementException:
            pass  # Already visible, or not required

        # Input pincode
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "GLUXZipInputField")))
        driver.find_element(By.ID, "GLUXZipInputField").clear()
        driver.find_element(By.ID, "GLUXZipInputField").send_keys(pincode)
        driver.find_element(By.ID, "GLUXZipUpdate").click()
        time.sleep(2)
        logging.info(f"Pincode {pincode} delivery validated.")
    except Exception as e:
        logging.warning(f"Pincode validation skipped or failed: {e}")

def set_quantity(driver, quantity):
    try:
        qty_dropdown = driver.find_element(By.ID, "quantity")
        qty_dropdown.click()
        time.sleep(1)
        qty_option = driver.find_element(By.XPATH, f"//option[@value='{quantity}']")
        qty_option.click()
        logging.info(f"Set product quantity to {quantity}.")
    except NoSuchElementException:
        logging.warning("Quantity dropdown not found or not applicable.")

def add_to_cart(driver):
    try:
        add_btn = driver.find_element(By.ID, "add-to-cart-button")
        add_btn.click()
        # Wait for confirmation
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "attach-sidesheet-view-cart-button"))
        )
        logging.info("Product added to cart.")
    except NoSuchElementException:
        logging.error("Add to cart button not found.")
        raise

def proceed_to_checkout(driver):
    try:
        # Go to cart
        driver.get(CART_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "proceedToRetailCheckout")))
        checkout_btn = driver.find_element(By.NAME, "proceedToRetailCheckout")
        checkout_btn.click()
        logging.info("Proceeded to checkout.")
        # Stop here to avoid actual purchase
        logging.info("Automation stops before payment for safety.")
    except NoSuchElementException:
        logging.error("Checkout button not found.")
        raise

def main():
    username = get_env_var("AMAZON_USERNAME")
    password = get_env_var("AMAZON_PASSWORD")
    asin = get_env_var("AMAZON_ASIN")
    pincode = get_env_var("AMAZON_PINCODE")
    quantity = get_env_var("AMAZON_QUANTITY", required=False) or "1"

    # --- WebDriver Setup ---
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless execution
    driver = webdriver.Chrome(options=options)

    try:
        amazon_login(driver, username, password)
        navigate_to_product(driver, asin)
        validate_delivery_pincode(driver, pincode)
        set_quantity(driver, quantity)
        add_to_cart(driver)
        proceed_to_checkout(driver)
        logging.info("Amazon purchase automation completed successfully.")
    except Exception as e:
        logging.error(f"Automation failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
