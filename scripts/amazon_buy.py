import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Configuration from environment variables
AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')
AMAZON_ASIN = os.getenv('AMAZON_ASIN', 'B088N8G9RL')
AMAZON_PINCODE = os.getenv('AMAZON_PINCODE', '560001')
AMAZON_QUANTITY = int(os.getenv('AMAZON_QUANTITY', '1'))

# Validate configuration
if not all([AMAZON_USERNAME, AMAZON_PASSWORD, AMAZON_ASIN, AMAZON_PINCODE, AMAZON_QUANTITY]):
    logging.error("Missing one or more required environment variables.")
    exit(1)

def init_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver

def login_amazon(driver, username, password):
    logging.info("Navigating to Amazon login page.")
    driver.get('https://www.amazon.in/')
    try:
        driver.find_element(By.ID, 'nav-link-accountList').click()
        driver.find_element(By.ID, 'ap_email').send_keys(username)
        driver.find_element(By.ID, 'continue').click()
        driver.find_element(By.ID, 'ap_password').send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()
        # Check for CAPTCHA/anti-bot
        if "auth-captcha-image" in driver.page_source:
            logging.error("CAPTCHA detected. Manual intervention required.")
            return False
        # Validate login success
        if driver.find_elements(By.ID, 'nav-link-accountList-nav-line-1'):
            logging.info("Login successful.")
            return True
        else:
            logging.error("Login failed. Check credentials.")
            return False
    except NoSuchElementException as e:
        logging.error(f"Login element not found: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during login: {e}")
        return False

def navigate_to_product(driver, asin):
    product_url = f'https://www.amazon.in/dp/{asin}'
    logging.info(f"Navigating to product page: {product_url}")
    driver.get(product_url)
    # Check if product page loaded
    time.sleep(3)
    if "Sorry, we couldn't find that page" in driver.page_source:
        logging.error("Product page not found. Check ASIN.")
        return False
    return True

def set_delivery_pincode(driver, pincode):
    try:
        # Check if pincode box exists
        if driver.find_elements(By.ID, 'contextualIngressPtPin'):
            driver.find_element(By.ID, 'contextualIngressPtPin').click()
            time.sleep(1)
            pin_input = driver.find_element(By.ID, 'GLUXZipUpdateInput')
            pin_input.clear()
            pin_input.send_keys(pincode)
            driver.find_element(By.ID, 'GLUXZipUpdate').click()
            time.sleep(2)
            logging.info(f"Delivery pincode set to {pincode}.")
        else:
            logging.info("Pincode selection not required or already set.")
        return True
    except NoSuchElementException:
        logging.warning("Pincode input not found; continuing.")
        return False

def add_to_cart(driver, quantity):
    try:
        # Set quantity if applicable
        if quantity > 1:
            qty_select = driver.find_element(By.ID, 'quantity')
            qty_select.click()
            qty_option = driver.find_element(By.XPATH, f"//option[@value='{quantity}']")
            qty_option.click()
            logging.info(f"Quantity set to {quantity}.")
        # Click add to cart
        driver.find_element(By.ID, 'add-to-cart-button').click()
        time.sleep(2)
        logging.info("Product added to cart.")
        return True
    except NoSuchElementException:
        logging.error("Add to cart button not found.")
        return False
    except Exception as e:
        logging.error(f"Error adding to cart: {e}")
        return False

def proceed_to_buy(driver):
    try:
        # Proceed to checkout
        if driver.find_elements(By.ID, 'hlb-ptc-btn-native'):
            driver.find_element(By.ID, 'hlb-ptc-btn-native').click()
            logging.info("Proceeded to checkout page.")
            return True
        elif driver.find_elements(By.NAME, 'proceedToRetailCheckout'):
            driver.find_element(By.NAME, 'proceedToRetailCheckout').click()
            logging.info("Proceeded to checkout page (alternate button).")
            return True
        else:
            logging.error("Proceed to buy button not found.")
            return False
    except NoSuchElementException:
        logging.error("Checkout button not found.")
        return False
    except Exception as e:
        logging.error(f"Error proceeding to buy: {e}")
        return False

def main():
    driver = None
    try:
        driver = init_driver(headless=False)  # Set True for CI/CD or silent execution
        # Step 1: Login
        if not login_amazon(driver, AMAZON_USERNAME, AMAZON_PASSWORD):
            logging.error("Automation stopped: Login failed.")
            return
        # Step 2: Navigate to Product
        if not navigate_to_product(driver, AMAZON_ASIN):
            logging.error("Automation stopped: Product navigation failed.")
            return
        # Step 3: Set Pincode
        set_delivery_pincode(driver, AMAZON_PINCODE)
        # Step 4: Add to Cart
        if not add_to_cart(driver, AMAZON_QUANTITY):
            logging.error("Automation stopped: Add to cart failed.")
            return
        # Step 5: Proceed to Buy
        if not proceed_to_buy(driver):
            logging.error("Automation stopped: Proceed to buy failed.")
            return
        logging.info("Purchase flow completed successfully up to checkout. Manual payment required.")
    except WebDriverException as e:
        logging.error(f"WebDriver error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if driver:
            driver.quit()
            logging.info("Browser closed.")

if __name__ == '__main__':
    main()
