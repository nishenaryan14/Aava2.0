"""
Amazon Automated Purchase Script
--------------------------------
Automates Amazon login and product purchase using Selenium WebDriver.
Parameters (set via environment variables):
- AMAZON_USERNAME: Amazon account email/username
- AMAZON_PASSWORD: Amazon account password
- AMAZON_ASIN: Product ASIN to purchase
- AMAZON_PINCODE: Delivery pincode (optional, for address selection)
- AMAZON_QUANTITY: Quantity to purchase (default: 1)

Setup:
1. Install Python 3.8+, Selenium (`pip install selenium`), and ChromeDriver (add to PATH).
2. Set environment variables as above.
3. Run: python amazon_purchase.py

Troubleshooting:
- Ensure credentials are correct.
- Update ChromeDriver if browser version changes.
- Check selectors if Amazon UI updates.
"""

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
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)

def get_env_var(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        logging.error(f"Environment variable '{name}' is required but not set.")
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value

def amazon_login(driver, username, password):
    logging.info("Navigating to Amazon login page.")
    driver.get('https://www.amazon.in/')  # Use .com for US, .in for India
    try:
        account_list = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'nav-link-accountList'))
        )
        account_list.click()

        email_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'ap_email'))
        )
        email_input.send_keys(username)
        driver.find_element(By.ID, 'continue').click()

        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'ap_password'))
        )
        password_input.send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()

        # Check for CAPTCHA
        time.sleep(2)
        if "authentication/captcha" in driver.current_url:
            logging.error("CAPTCHA detected. Manual intervention required.")
            raise Exception("CAPTCHA encountered during login.")

        logging.info("Login successful.")
        return True
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Login failed: {e}")
        return False

def navigate_to_product(driver, asin):
    logging.info(f"Navigating to product page for ASIN: {asin}")
    product_url = f"https://www.amazon.in/dp/{asin}"
    driver.get(product_url)
    try:
        # Wait for add-to-cart button
        add_to_cart_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'add-to-cart-button'))
        )
        logging.info("Product page loaded successfully.")
        return True
    except (NoSuchElementException, TimeoutException):
        logging.error("Product not found or add-to-cart button missing.")
        return False

def set_quantity(driver, quantity):
    try:
        if quantity and int(quantity) > 1:
            qty_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'quantity'))
            )
            qty_dropdown.click()
            qty_option = driver.find_element(By.XPATH, f"//option[@value='{quantity}']")
            qty_option.click()
            logging.info(f"Quantity set to {quantity}.")
        else:
            logging.info("Default quantity (1) selected.")
    except Exception as e:
        logging.warning(f"Could not set quantity: {e}")

def add_to_cart(driver):
    try:
        add_to_cart_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'add-to-cart-button'))
        )
        add_to_cart_btn.click()
        logging.info("Product added to cart.")
        # Wait for cart confirmation
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'attach-sidesheet-checkout-button'))
        )
        return True
    except Exception as e:
        logging.error(f"Failed to add product to cart: {e}")
        return False

def proceed_to_checkout(driver):
    try:
        checkout_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'attach-sidesheet-checkout-button'))
        )
        checkout_btn.click()
        logging.info("Proceeded to checkout.")
        return True
    except Exception as e:
        logging.warning(f"Checkout button not found in sidesheet, trying alternate flow: {e}")
        try:
            # Try alternate checkout button
            driver.get("https://www.amazon.in/gp/cart/view.html")
            ptc_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, 'proceedToRetailCheckout'))
            )
            ptc_btn.click()
            logging.info("Proceeded to checkout via cart page.")
            return True
        except Exception as ex:
            logging.error(f"Failed to proceed to checkout: {ex}")
            return False

def select_address(driver, pincode):
    try:
        # On first purchase, Amazon may prompt for address selection
        logging.info(f"Selecting delivery address for pincode: {pincode}")
        # This step can be customized based on actual page elements
        # Example: driver.find_element(By.XPATH, "//input[@placeholder='Enter pincode']").send_keys(pincode)
        # driver.find_element(By.XPATH, "//span[text()='Apply']").click()
        logging.info("Address selection step skipped (customize as needed).")
    except Exception as e:
        logging.warning(f"Address selection failed/skipped: {e}")

def main():
    username = get_env_var('AMAZON_USERNAME', required=True)
    password = get_env_var('AMAZON_PASSWORD', required=True)
    asin = get_env_var('AMAZON_ASIN', required=True)
    pincode = get_env_var('AMAZON_PINCODE', default=None)
    quantity = get_env_var('AMAZON_QUANTITY', default='1')

    # Start WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # Uncomment for headless execution
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        if not amazon_login(driver, username, password):
            logging.error("Aborting: Login unsuccessful.")
            return

        if not navigate_to_product(driver, asin):
            logging.error("Aborting: Product navigation unsuccessful.")
            return

        set_quantity(driver, quantity)
        if not add_to_cart(driver):
            logging.error("Aborting: Add to cart unsuccessful.")
            return

        if not proceed_to_checkout(driver):
            logging.error("Aborting: Checkout unsuccessful.")
            return

        if pincode:
            select_address(driver, pincode)

        logging.info("Amazon purchase flow completed up to checkout. (Payment step not automated for security.)")
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
    finally:
        driver.quit()
        logging.info("WebDriver session ended.")

if __name__ == '__main__':
    main()
