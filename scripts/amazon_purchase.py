import os
import sys
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# --- Configuration ---
AMAZON_USERNAME = os.getenv("AMAZON_USERNAME")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")
ASIN = os.getenv("AMAZON_ASIN", "B088N8G9RL")
SEARCH_TERM = os.getenv("AMAZON_SEARCH_TERM", "Logitech wireless mouse")
PINCODE = os.getenv("AMAZON_PINCODE", "560001")
QUANTITY = int(os.getenv("AMAZON_QUANTITY", 1))

# --- Utility Functions ---
def validate_env():
    """Ensure all required environment variables are set."""
    missing = []
    for var in ["AMAZON_USERNAME", "AMAZON_PASSWORD"]:
        if not os.getenv(var):
            missing.append(var)
    if missing:
        logging.error(f"Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

def get_product_url(asin):
    """Construct Amazon product URL from ASIN."""
    return f"https://www.amazon.in/dp/{asin}"

def wait_for_element(driver, by, value, timeout=15):
    """Wait for element to be present."""
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        logging.error(f"Timeout waiting for element: {value}")
        return None

def safe_click(driver, by, value):
    """Safely click an element if present."""
    try:
        elem = wait_for_element(driver, by, value)
        if elem:
            elem.click()
            return True
        else:
            logging.error(f"Element not found for clicking: {value}")
            return False
    except Exception as e:
        logging.error(f"Error clicking element {value}: {e}")
        return False

# --- Main Automation Steps ---
def amazon_login(driver, username, password):
    """Login to Amazon account."""
    driver.get("https://www.amazon.in/")
    safe_click(driver, By.ID, "nav-link-accountList")
    email_field = wait_for_element(driver, By.ID, "ap_email")
    if not email_field:
        raise Exception("Email field not found.")
    email_field.clear()
    email_field.send_keys(username)
    safe_click(driver, By.ID, "continue")
    pwd_field = wait_for_element(driver, By.ID, "ap_password")
    if not pwd_field:
        raise Exception("Password field not found.")
    pwd_field.clear()
    pwd_field.send_keys(password)
    safe_click(driver, By.ID, "signInSubmit")
    # Check for login errors or CAPTCHA
    time.sleep(2)
    if "authentication" in driver.current_url or "ap/cvf" in driver.current_url:
        raise Exception("Login failed or CAPTCHA encountered.")
    logging.info("Login successful.")

def set_delivery_pincode(driver, pincode):
    """Set delivery pincode if prompted."""
    try:
        # Sometimes Amazon prompts for pincode on product page
        pincode_btn = driver.find_elements(By.ID, "contextualIngressPtLabel_deliveryShortLine")
        if pincode_btn:
            pincode_btn[0].click()
            pincode_input = wait_for_element(driver, By.ID, "GLUXZipUpdateInput")
            if pincode_input:
                pincode_input.clear()
                pincode_input.send_keys(pincode)
                safe_click(driver, By.ID, "GLUXZipUpdate")
                time.sleep(2)
                logging.info(f"Pincode {pincode} set.")
    except Exception as e:
        logging.warning(f"Pincode set skipped: {e}")

def add_to_cart(driver, quantity=1):
    """Add product to cart with specified quantity."""
    # Set quantity if applicable
    try:
        qty_dropdown = driver.find_elements(By.ID, "quantity")
        if qty_dropdown:
            qty_dropdown[0].send_keys(str(quantity))
            logging.info(f"Quantity set to {quantity}.")
    except Exception as e:
        logging.warning(f"Unable to set quantity: {e}")
    # Click Add to Cart
    if not safe_click(driver, By.ID, "add-to-cart-button"):
        raise Exception("Add to cart button not found.")
    time.sleep(2)
    # Handle side cart popups
    try:
        safe_click(driver, By.ID, "attach-sidesheet-view-cart-button")
    except Exception:
        pass

def proceed_to_checkout(driver):
    """Proceed to checkout."""
    # Sometimes checkout button is different
    if not safe_click(driver, By.ID, "hlb-ptc-btn-native"):
        if not safe_click(driver, By.NAME, "proceedToRetailCheckout"):
            raise Exception("Proceed to checkout button not found.")
    logging.info("Proceeded to checkout.")
    time.sleep(2)

def finalize_order(driver):
    """Finalize the order. For security, stops before payment confirmation."""
    # This step depends on saved address/payment. For demo, stop at review order.
    try:
        # Select address if prompted
        address_buttons = driver.find_elements(By.NAME, "shipToThisAddress")
        if address_buttons:
            address_buttons[0].click()
            time.sleep(2)
        # Select payment method if prompted (skipped for demo)
        # Stop at 'Place your order' page
        logging.info("Reached order review page. Manual confirmation required for payment.")
    except Exception as e:
        logging.warning(f"Finalize order step: {e}")

def amazon_purchase_flow(username, password, asin, pincode, quantity):
    """Complete Amazon purchase flow."""
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless") # Uncomment for headless execution
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        amazon_login(driver, username, password)
        product_url = get_product_url(asin)
        driver.get(product_url)
        set_delivery_pincode(driver, pincode)
        add_to_cart(driver, quantity)
        proceed_to_checkout(driver)
        finalize_order(driver)
        logging.info("Automation flow completed. Review order manually before payment.")
    except Exception as e:
        logging.error(f"Automation failed: {e}")
    finally:
        if driver:
            driver.quit()

# --- Usage Example & Entry Point ---
if __name__ == "__main__":
    """
    Usage:
      Set environment variables:
        - AMAZON_USERNAME: Amazon account username/email
        - AMAZON_PASSWORD: Amazon account password
        - AMAZON_ASIN: Product ASIN (default: B088N8G9RL)
        - AMAZON_PINCODE: Delivery pincode (default: 560001)
        - AMAZON_QUANTITY: Quantity to purchase (default: 1)
      Run:
        python amazon_purchase.py
    """
    validate_env()
    amazon_purchase_flow(
        AMAZON_USERNAME,
        AMAZON_PASSWORD,
        ASIN,
        PINCODE,
        QUANTITY,
    )