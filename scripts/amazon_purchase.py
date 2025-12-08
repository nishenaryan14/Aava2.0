import os
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

# Configure logging
logging.basicConfig(
    filename='amazon_purchase.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Load credentials and parameters from environment
AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')
AMAZON_ASIN = os.getenv('AMAZON_ASIN', 'B088N8G9RL')
AMAZON_PINCODE = os.getenv('AMAZON_PINCODE', '560001')

def amazon_login_and_purchase(username, password, asin, pincode):
    """
    Automates Amazon login, product search by ASIN, delivery pincode set,
    add to cart, and purchase initiation.
    """
    # Validate input
    if not all([username, password, asin, pincode]):
        logging.error("Missing required parameters.")
        print("Error: Missing required parameters. Check environment variables.")
        return

    # Set up Selenium WebDriver (Chrome)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Uncomment for headless execution:
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        logging.info("Navigating to Amazon homepage.")
        driver.get('https://www.amazon.in/')
        time.sleep(2)

        # Click 'Sign In'
        try:
            sign_in_btn = wait.until(EC.element_to_be_clickable((By.ID, 'nav-link-accountList')))
            sign_in_btn.click()
        except TimeoutException:
            logging.error("Sign in button not found.")
            print("Error: Sign in button not found.")
            return

        # Enter username
        email_input = wait.until(EC.presence_of_element_located((By.ID, 'ap_email')))
        email_input.send_keys(username)
        driver.find_element(By.ID, 'continue').click()

        # Enter password
        password_input = wait.until(EC.presence_of_element_located((By.ID, 'ap_password')))
        password_input.send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()
        time.sleep(3)

        # Check for CAPTCHA
        if "authentication required" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
            logging.error("CAPTCHA detected. Manual intervention required.")
            print("Error: CAPTCHA detected. Manual intervention required.")
            return

        logging.info("Login successful.")

        # Navigate to product page by ASIN
        product_url = f'https://www.amazon.in/dp/{asin}'
        logging.info(f"Navigating to product page: {product_url}")
        driver.get(product_url)
        time.sleep(2)

        # Set delivery pincode
        try:
            pincode_box = wait.until(EC.element_to_be_clickable((By.ID, 'contextualIngressPtLabel')))
            pincode_box.click()
            time.sleep(1)
            pincode_input = wait.until(EC.presence_of_element_located((By.ID, 'GLUXZipUpdateInput')))
            pincode_input.clear()
            pincode_input.send_keys(pincode)
            driver.find_element(By.ID, 'GLUXZipUpdate').click()
            time.sleep(2)
            logging.info(f"Pincode {pincode} set successfully.")
        except Exception as e:
            logging.warning(f"Pincode setting failed: {e}")

        # Add to cart
        try:
            add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.ID, 'add-to-cart-button')))
            add_to_cart_btn.click()
            logging.info("Product added to cart.")
            time.sleep(2)
        except TimeoutException:
            logging.error("Add to Cart button not found.")
            print("Error: Add to Cart button not found.")
            return

        # Proceed to checkout
        try:
            proceed_btn = wait.until(EC.element_to_be_clickable((By.ID, 'hlb-ptc-btn-native')))
            proceed_btn.click()
            logging.info("Proceeded to checkout.")
            print("Purchase flow completed up to checkout.")
        except TimeoutException:
            logging.error("Proceed to Checkout button not found.")
            print("Error: Proceed to Checkout button not found.")
            return

    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        logging.error(f"Automation error: {e}")
        print(f"Error during automation: {e}")
    finally:
        driver.quit()
        logging.info("WebDriver closed.")

if __name__ == '__main__':
    """
    Usage:
    - Set environment variables: AMAZON_USERNAME, AMAZON_PASSWORD, AMAZON_ASIN, AMAZON_PINCODE
    - Run: python amazon_purchase.py
    - Review 'amazon_purchase.log' for detailed execution logs.
    """
    amazon_login_and_purchase(AMAZON_USERNAME, AMAZON_PASSWORD, AMAZON_ASIN, AMAZON_PINCODE)
