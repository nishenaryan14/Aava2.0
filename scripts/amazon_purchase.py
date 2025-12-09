import os
import time
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
from dotenv import load_dotenv

# Load environment variables from .env file for credentials and product details
load_dotenv()
AMAZON_USERNAME = os.getenv("AMAZON_USERNAME")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")
AMAZON_ASIN = os.getenv("AMAZON_ASIN", "B088N8G9RL")
AMAZON_PINCODE = os.getenv("AMAZON_PINCODE", "560001")

# Product URL template
PRODUCT_URL = f"https://www.amazon.in/dp/{AMAZON_ASIN}"

def log(message):
    print(f"[AmazonAutomation] {message}")

def amazon_login(driver, username, password):
    try:
        driver.get("https://www.amazon.in/")
        log("Navigated to Amazon homepage.")
        sign_in_elem = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "nav-link-accountList"))
        )
        sign_in_elem.click()
        log("Clicked Sign-In link.")

        email_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_elem.send_keys(username)
        driver.find_element(By.ID, "continue").click()
        log("Entered username and clicked Continue.")

        password_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_elem.send_keys(password)
        driver.find_element(By.ID, "signInSubmit").click()
        log("Entered password and signed in.")

        # Check for login errors or CAPTCHAs
        time.sleep(2)
        if "authentication required" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
            log("Login failed due to CAPTCHA or authentication challenge.")
            return False

        log("Login successful.")
        return True
    except (NoSuchElementException, TimeoutException) as e:
        log(f"Error during login: {e}")
        return False

def set_delivery_pincode(driver, pincode):
    try:
        driver.get(PRODUCT_URL)
        log(f"Navigated to product page: {PRODUCT_URL}")

        # Wait for location/pincode element and click to change
        try:
            deliver_elem = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "contextualIngressPtLabel_deliveryShortLine"))
            )
            deliver_elem.click()
            log("Clicked delivery location link.")
        except TimeoutException:
            log("Delivery location link not found, trying alternate method.")

        # Enter pincode
        pincode_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput"))
        )
        pincode_input.clear()
        pincode_input.send_keys(pincode)
        driver.find_element(By.ID, "GLUXZipUpdate").click()
        log(f"Set delivery pincode to {pincode}.")

        # Wait for pincode update confirmation
        time.sleep(2)
        return True
    except (NoSuchElementException, TimeoutException) as e:
        log(f"Error setting delivery pincode: {e}")
        return False

def add_to_cart_and_checkout(driver):
    try:
        # Ensure we're on the product page
        driver.get(PRODUCT_URL)
        log("Ensured on product page for cart addition.")

        # Add to cart
        add_to_cart_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
        )
        add_to_cart_btn.click()
        log("Clicked Add to Cart.")

        # Wait for cart confirmation
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "attach-sidesheet-view-cart-button"))
        )
        log("Product added to cart.")

        # Proceed to checkout
        proceed_btn = None
        try:
            proceed_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "hlb-ptc-btn-native"))
            )
        except TimeoutException:
            # Try alternate selector
            proceed_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "proceedToRetailCheckout"))
            )
        proceed_btn.click()
        log("Proceeded to checkout.")

        # Note: Address and payment steps may require manual intervention or further automation
        log("Purchase flow (until checkout) completed successfully.")
        return True
    except (NoSuchElementException, TimeoutException) as e:
        log(f"Error during add to cart/checkout: {e}")
        return False

def main():
    # Validate required inputs
    if not AMAZON_USERNAME or not AMAZON_PASSWORD:
        log("Amazon credentials are missing. Please set in environment or .env file.")
        return
    options = webdriver.ChromeOptions()
    # Uncomment the following line for headless execution
    # options.add_argument("--headless")
    try:
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        log("Chrome browser launched.")

        if not amazon_login(driver, AMAZON_USERNAME, AMAZON_PASSWORD):
            log("Login failed. Exiting.")
            driver.quit()
            return

        if not set_delivery_pincode(driver, AMAZON_PINCODE):
            log("Failed to set delivery pincode. Exiting.")
            driver.quit()
            return

        if not add_to_cart_and_checkout(driver):
            log("Failed during add to cart or checkout. Exiting.")
            driver.quit()
            return

        log("Amazon automation script completed successfully.")
    except WebDriverException as e:
        log(f"WebDriver error: {e}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()
