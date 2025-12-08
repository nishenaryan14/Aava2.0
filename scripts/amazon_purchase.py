import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    WebDriverException
)
from selenium.webdriver.chrome.options import Options

# --- Configuration ---
logging.basicConfig(
    filename='amazon_purchase.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

AMAZON_URL = "https://www.amazon.in/"
LOGIN_URL = "https://www.amazon.in/ap/signin"
PRODUCT_URL_TEMPLATE = "https://www.amazon.in/dp/{asin}"

# --- Utility Functions ---
def get_env_var(var_name, required=True):
    value = os.getenv(var_name)
    if required and not value:
        logging.error(f"Missing required environment variable: {var_name}")
        raise ValueError(f"Missing required environment variable: {var_name}")
    return value

def wait_and_find(driver, by, value, timeout=10):
    for _ in range(timeout):
        try:
            element = driver.find_element(by, value)
            return element
        except NoSuchElementException:
            time.sleep(1)
    logging.error(f"Element not found: {value}")
    raise NoSuchElementException(f"Element not found: {value}")

# --- Main Automation Workflow ---
def amazon_login_and_buy():
    username = get_env_var('AMAZON_USERNAME')
    password = get_env_var('AMAZON_PASSWORD')
    asin = get_env_var('AMAZON_ASIN')
    pincode = get_env_var('AMAZON_PINCODE')
    quantity = int(get_env_var('AMAZON_QUANTITY', required=False) or "1")
    product_url = PRODUCT_URL_TEMPLATE.format(asin=asin)

    # Optional: Run Chrome in headless mode for CI/CD
    chrome_options = Options()
    # Uncomment the next line for headless execution
    # chrome_options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        logging.info("Navigating to Amazon homepage")
        driver.get(AMAZON_URL)

        # Click 'Sign In'
        try:
            sign_in_elem = wait_and_find(driver, By.ID, "nav-link-accountList")
            sign_in_elem.click()
        except Exception as e:
            logging.error("Sign-in button not found")
            raise

        # Login flow
        logging.info("Attempting login")
        email_elem = wait_and_find(driver, By.ID, "ap_email")
        email_elem.send_keys(username)
        driver.find_element(By.ID, "continue").click()

        password_elem = wait_and_find(driver, By.ID, "ap_password")
        password_elem.send_keys(password)
        driver.find_element(By.ID, "signInSubmit").click()

        # Validate login success
        time.sleep(3)
        if "authentication" in driver.current_url or "ap/signin" in driver.current_url:
            logging.error("Login failed: Check credentials or CAPTCHA triggered")
            print("Login failed. Check credentials or CAPTCHA challenge.")
            return

        # Go to product page by ASIN
        logging.info(f"Navigating to product: {product_url}")
        driver.get(product_url)
        time.sleep(2)

        # Check and enter pincode for delivery availability
        try:
            pincode_box = driver.find_element(By.ID, "contextualIngressPtLabel_deliveryShortLine")
            pincode_box.click()
            pincode_input = wait_and_find(driver, By.ID, "GLUXZipUpdateInput")
            pincode_input.clear()
            pincode_input.send_keys(pincode)
            driver.find_element(By.ID, "GLUXZipUpdate").click()
            time.sleep(2)
        except NoSuchElementException:
            logging.warning("Pincode entry skipped: Element not found (maybe not required)")
        
        # Set quantity
        try:
            qty_dropdown = driver.find_element(By.ID, "quantity")
            qty_dropdown.click()
            qty_option = driver.find_element(By.XPATH, f"//option[@value='{quantity}']")
            qty_option.click()
        except NoSuchElementException:
            logging.info("Quantity dropdown not found, proceeding with default quantity=1")

        # Add to cart
        try:
            add_to_cart_btn = wait_and_find(driver, By.ID, "add-to-cart-button")
            add_to_cart_btn.click()
            logging.info("Product added to cart")
            time.sleep(3)
        except Exception as e:
            logging.error("Add to cart failed")
            print("Could not add product to cart.")
            return

        # Proceed to checkout
        try:
            proceed_btn = wait_and_find(driver, By.ID, "hlb-ptc-btn-native")
            proceed_btn.click()
            logging.info("Proceeded to checkout")
        except NoSuchElementException:
            logging.error("Checkout button not found")
            print("Could not proceed to checkout.")
            return

        # NOTE: Payment and address selection steps are not automated for security.
        print("Amazon purchase flow completed up to checkout page.")
        logging.info("Purchase flow completed up to checkout page.")
    except (NoSuchElementException, TimeoutException, ElementClickInterceptedException, WebDriverException) as e:
        logging.error(f"Error during automation: {e}")
        print(f"Error during automation: {e}")
    finally:
        driver.quit()

# --- Entry Point ---
if __name__ == '__main__':
    amazon_login_and_buy()
