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

# --- Configuration ---
AMAZON_URL = 'https://www.amazon.in/'
USERNAME = os.getenv('AMAZON_USERNAME')
PASSWORD = os.getenv('AMAZON_PASSWORD')
ASIN = os.getenv('AMAZON_ASIN', 'B088N8G9RL')  # Default to Logitech wireless mouse ASIN
PINCODE = os.getenv('AMAZON_PINCODE', '560001')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# --- Logging Setup ---
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def wait_and_click(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()
        logging.info(f"Clicked element by {by}='{value}'")
        return True
    except TimeoutException:
        logging.error(f"Timeout: Element by {by}='{value}' not clickable.")
        return False

def wait_and_send_keys(driver, by, value, text, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        element.clear()
        element.send_keys(text)
        logging.info(f"Sent keys to element by {by}='{value}'")
        return True
    except TimeoutException:
        logging.error(f"Timeout: Element by {by}='{value}' not found.")
        return False

def amazon_login(driver, username, password):
    driver.get(AMAZON_URL)
    wait_and_click(driver, By.ID, 'nav-link-accountList')
    if not wait_and_send_keys(driver, By.ID, 'ap_email', username):
        raise Exception('Login: Email field not found.')
    wait_and_click(driver, By.ID, 'continue')
    if not wait_and_send_keys(driver, By.ID, 'ap_password', password):
        raise Exception('Login: Password field not found.')
    wait_and_click(driver, By.ID, 'signInSubmit')
    # Check for login error
    time.sleep(2)
    if "authentication" in driver.current_url or "ap/signin" in driver.current_url:
        logging.error("Login failed. Check credentials or CAPTCHA.")
        raise Exception("Login failed.")

def set_delivery_pincode(driver, pincode):
    try:
        # Click location/pincode edit (usually near top or product page)
        # On product page, "Deliver to" is often By.ID='contextualIngressPtLabel'
        wait_and_click(driver, By.ID, 'contextualIngressPtLabel', timeout=7)
        # Wait for pincode modal
        wait_and_send_keys(driver, By.ID, 'GLUXZipUpdateInput', pincode)
        wait_and_click(driver, By.ID, 'GLUXZipUpdate', timeout=7)
        time.sleep(2)
        logging.info(f"Delivery pincode set to {pincode}")
    except Exception as e:
        logging.warning(f"Could not set delivery pincode: {e}")

def add_product_to_cart(driver, asin):
    product_url = f'https://www.amazon.in/dp/{asin}'
    driver.get(product_url)
    time.sleep(2)
    set_delivery_pincode(driver, PINCODE)
    # Add to cart
    if not wait_and_click(driver, By.ID, 'add-to-cart-button', timeout=10):
        raise Exception('Add to Cart: Button not found.')
    time.sleep(2)
    # Proceed to cart/checkout
    try:
        wait_and_click(driver, By.ID, 'hlb-ptc-btn-native', timeout=10)  # Proceed to checkout
    except Exception:
        # Sometimes the ID is different or requires navigation to cart
        logging.warning("Proceed to checkout button not found. Navigating to cart.")
        driver.get('https://www.amazon.in/gp/cart/view.html')
        wait_and_click(driver, By.NAME, 'proceedToRetailCheckout', timeout=10)
    logging.info("Product added to cart and proceeded to checkout.")

def main():
    if not USERNAME or not PASSWORD:
        logging.error('Amazon credentials not set in environment variables.')
        return
    driver = None
    try:
        # Optionally, set options for headless execution
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Uncomment for headless mode
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        amazon_login(driver, USERNAME, PASSWORD)
        add_product_to_cart(driver, ASIN)
        logging.info('Amazon purchase flow completed successfully.')
    except WebDriverException as wde:
        logging.error(f'WebDriver error: {wde}')
    except Exception as e:
        logging.error(f'Error during automation: {e}')
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    main()
