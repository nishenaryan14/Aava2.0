import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables for credentials and pincode
load_dotenv()
AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')
AMAZON_PINCODE = os.getenv('AMAZON_PINCODE', '560001')
ASIN = 'B088N8G9RL'
PRODUCT_URL = f"https://www.amazon.in/dp/{ASIN}"

def log(message):
    print(f"[INFO] {message}")

def amazon_login(driver, username, password):
    """Login to Amazon account securely."""
    try:
        driver.get('https://www.amazon.in/')
        log("Navigated to Amazon homepage.")
        driver.find_element(By.ID, 'nav-link-accountList').click()
        log("Clicked on 'Sign In'.")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ap_email')))
        driver.find_element(By.ID, 'ap_email').send_keys(username)
        driver.find_element(By.ID, 'continue').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ap_password')))
        driver.find_element(By.ID, 'ap_password').send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()
        log("Submitted login credentials.")
        # Optional: Wait for login success (check for user greeting or account menu)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'nav-link-accountList')))
        log("Login successful.")
        return True
    except Exception as e:
        log(f"Login failed: {e}")
        return False

def set_delivery_pincode(driver, pincode):
    """Set delivery location to specified pincode."""
    try:
        # On product page, set delivery pincode
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'contextualIngressPtLabel')))
        driver.find_element(By.ID, 'contextualIngressPtLabel').click()
        log("Opened delivery location dialog.")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'GLUXZipUpdateInput')))
        zip_input = driver.find_element(By.ID, 'GLUXZipUpdateInput')
        zip_input.clear()
        zip_input.send_keys(pincode)
        driver.find_element(By.ID, 'GLUXZipUpdate').click()
        log(f"Set delivery pincode to {pincode}.")
        # Wait for update
        time.sleep(2)
    except Exception as e:
        log(f"Failed to set delivery pincode: {e}")

def add_product_to_cart(driver):
    """Add specified product to cart."""
    try:
        # Wait for product page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'add-to-cart-button')))
        driver.find_element(By.ID, 'add-to-cart-button').click()
        log("Clicked 'Add to Cart'.")
        # Wait for cart confirmation
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'attach-sidesheet-view-cart-button')))
        log("Product added to cart.")
        return True
    except Exception as e:
        log(f"Add to cart failed: {e}")
        return False

def proceed_to_checkout(driver):
    """Proceed to checkout."""
    try:
        driver.find_element(By.ID, 'attach-sidesheet-view-cart-button').click()
        log("Navigated to cart.")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'proceedToRetailCheckout')))
        driver.find_element(By.NAME, 'proceedToRetailCheckout').click()
        log("Proceeded to checkout.")
        # Additional steps (address selection, payment) may be required
        return True
    except Exception as e:
        log(f"Checkout failed: {e}")
        return False

def main():
    # Validate input completeness
    if not (AMAZON_USERNAME and AMAZON_PASSWORD):
        log("Amazon credentials are missing. Set AMAZON_USERNAME and AMAZON_PASSWORD in environment.")
        return
    driver = None
    try:
        driver = webdriver.Chrome()  # Or use webdriver.Firefox() as required
        driver.maximize_window()
        # Step 1: Login
        if not amazon_login(driver, AMAZON_USERNAME, AMAZON_PASSWORD):
            log("Exiting due to login failure.")
            return
        # Step 2: Navigate to product page
        driver.get(PRODUCT_URL)
        log(f"Opened product page: {PRODUCT_URL}")
        # Step 3: Set delivery pincode
        set_delivery_pincode(driver, AMAZON_PINCODE)
        # Step 4: Add to cart
        if not add_product_to_cart(driver):
            log("Exiting due to add-to-cart failure.")
            return
        # Step 5: Proceed to checkout
        if not proceed_to_checkout(driver):
            log("Exiting due to checkout failure.")
            return
        log("Purchase flow completed successfully (up to checkout).")
    except WebDriverException as e:
        log(f"Selenium WebDriver error: {e}")
    finally:
        if driver:
            driver.quit()
        log("WebDriver session closed.")

if __name__ == '__main__':
    main()
