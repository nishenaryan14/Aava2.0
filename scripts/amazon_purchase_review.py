
"""
Amazon Purchase Review Automation Script
---------------------------------------
Automates login, product navigation (ASIN), delivery pincode selection, cart addition,
and checkout review on Amazon (without placing a real order).

Setup:
1. Install dependencies:
    pip install selenium python-dotenv
2. Download ChromeDriver and ensure it matches your Chrome browser version.
3. Create a .env file in the script directory with:
    AMAZON_USERNAME=your_email@example.com
    AMAZON_PASSWORD=your_amazon_password
    AMAZON_ASIN=B088N8G9RL
    AMAZON_PINCODE=560001

Usage:
    python amazon_purchase_review.py

Troubleshooting:
- Check logs for error details.
- Update selectors if Amazon UI changes.
- Rotate credentials securely.

Author: Senior Test Automation Engineer
Date: 2024-06
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AMAZON_USERNAME = os.getenv("AMAZON_USERNAME")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")
AMAZON_ASIN = os.getenv("AMAZON_ASIN")
AMAZON_PINCODE = os.getenv("AMAZON_PINCODE")

# Configure logging
logging.basicConfig(
    filename="amazon_purchase_review.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def amazon_login(driver, username, password):
    try:
        driver.get("https://www.amazon.in/")
        logging.info("Navigated to Amazon homepage.")
        driver.find_element(By.ID, "nav-link-accountList").click()
        driver.find_element(By.ID, "ap_email").send_keys(username)
        driver.find_element(By.ID, "continue").click()
        driver.find_element(By.ID, "ap_password").send_keys(password)
        driver.find_element(By.ID, "signInSubmit").click()
        logging.info("Logged in successfully.")
        time.sleep(2)
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Login failed: {e}")
        raise

def navigate_to_product(driver, asin):
    try:
        product_url = f"https://www.amazon.in/dp/{asin}"
        driver.get(product_url)
        logging.info(f"Navigated to product page: {product_url}")
        time.sleep(2)
    except Exception as e:
        logging.error(f"Product navigation failed: {e}")
        raise

def set_delivery_pincode(driver, pincode):
    try:
        # Try finding the pincode input on the product page
        try:
            pincode_button = driver.find_element(By.ID, "contextualIngressPtLabel_deliveryShortLine")
            pincode_button.click()
            time.sleep(1)
        except NoSuchElementException:
            logging.warning("Pincode button not found, may already be set.")

        pincode_input = driver.find_element(By.ID, "GLUXZipUpdateInput")
        pincode_input.clear()
        pincode_input.send_keys(pincode)
        driver.find_element(By.ID, "GLUXZipUpdate").click()
        time.sleep(2)
        logging.info(f"Set delivery pincode to {pincode}.")
    except NoSuchElementException:
        logging.warning("Pincode input not found, delivery location may not be changeable.")
    except Exception as e:
        logging.error(f"Setting pincode failed: {e}")
        raise

def add_to_cart(driver):
    try:
        add_cart_btn = driver.find_element(By.ID, "add-to-cart-button")
        add_cart_btn.click()
        logging.info("Product added to cart.")
        time.sleep(2)
        # Handle possible popups
        try:
            no_thanks_btn = driver.find_element(By.XPATH, "//input[@aria-labelledby='attachSiNoCoverage-announce']")
            no_thanks_btn.click()
            logging.info("No warranty popup handled.")
            time.sleep(1)
        except NoSuchElementException:
            pass
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        logging.error(f"Add to cart failed: {e}")
        raise

def proceed_to_checkout_review(driver):
    try:
        # Go to cart
        driver.get("https://www.amazon.in/gp/cart/view.html")
        time.sleep(2)
        # Proceed to checkout review (do not place order)
        proceed_btn = driver.find_element(By.NAME, "proceedToRetailCheckout")
        proceed_btn.click()
        logging.info("Proceeded to checkout review page.")
        time.sleep(3)
        # Scrape price, delivery, payment options (for review only)
        try:
            price = driver.find_element(By.CSS_SELECTOR, ".grand-total-price").text
            logging.info(f"Order Total: {price}")
        except NoSuchElementException:
            logging.warning("Order total not found.")

        try:
            delivery_option = driver.find_element(By.CSS_SELECTOR, ".a-row.address-row").text
            logging.info(f"Delivery Address: {delivery_option}")
        except NoSuchElementException:
            logging.warning("Delivery address not found.")

        try:
            payment_methods = driver.find_elements(By.CSS_SELECTOR, ".pmts-instrument-box")
            for idx, pm in enumerate(payment_methods):
                logging.info(f"Payment Method {idx+1}: {pm.text}")
        except NoSuchElementException:
            logging.warning("Payment methods not found.")

        print("Checkout review completed. Please verify in logs.")
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Checkout review failed: {e}")
        raise

def main():
    # Validate required inputs
    if not all([AMAZON_USERNAME, AMAZON_PASSWORD, AMAZON_ASIN, AMAZON_PINCODE]):
        print("Missing required environment variables. Check .env file.")
        logging.error("Missing required environment variables.")
        return

    # Chrome options for headless execution and anti-bot mitigation
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # Uncomment for headless execution
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    try:
        amazon_login(driver, AMAZON_USERNAME, AMAZON_PASSWORD)
        navigate_to_product(driver, AMAZON_ASIN)
        set_delivery_pincode(driver, AMAZON_PINCODE)
        add_to_cart(driver)
        proceed_to_checkout_review(driver)
        logging.info("Amazon purchase review flow completed successfully.")
    except Exception as e:
        print(f"Automation error: {e}. See logs for details.")
        logging.error(f"Automation error: {e}")
    finally:
        driver.quit()
        logging.info("WebDriver closed.")

if __name__ == "__main__":
    main()
