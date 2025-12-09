import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration & Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

AMAZON_USERNAME = os.getenv("AMAZON_USERNAME")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")
AMAZON_ASIN = os.getenv("AMAZON_ASIN", "B088N8G9RL")  # Default to Logitech mouse ASIN
AMAZON_PINCODE = os.getenv("AMAZON_PINCODE", "560001")
AMAZON_URL = f"https://www.amazon.in/dp/{AMAZON_ASIN}"

# --- Utility Functions ---
def wait_for_element(driver, by, value, timeout=15):
    """Wait for an element to be present and return it, else raise exception."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

# --- Main Automation Function ---
def amazon_login_and_purchase():
    if not AMAZON_USERNAME or not AMAZON_PASSWORD:
        logging.error("Amazon credentials not set in environment variables.")
        return

    options = Options()
    # Uncomment below for headless execution
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)

    try:
        logging.info("Navigating to Amazon homepage...")
        driver.get("https://www.amazon.in/")
        time.sleep(2)

        # Click 'Sign In'
        try:
            sign_in_elem = wait_for_element(driver, By.ID, "nav-link-accountList")
            sign_in_elem.click()
        except TimeoutException:
            logging.error("Sign-in element not found.")
            return

        # Enter username/email
        try:
            email_elem = wait_for_element(driver, By.ID, "ap_email")
            email_elem.clear()
            email_elem.send_keys(AMAZON_USERNAME)
            driver.find_element(By.ID, "continue").click()
        except TimeoutException:
            logging.error("Email input not found.")
            return

        # Enter password
        try:
            password_elem = wait_for_element(driver, By.ID, "ap_password")
            password_elem.clear()
            password_elem.send_keys(AMAZON_PASSWORD)
            driver.find_element(By.ID, "signInSubmit").click()
            time.sleep(2)
        except TimeoutException:
            logging.error("Password input not found.")
            return

        # Navigate directly to product page via ASIN
        logging.info(f"Navigating to product page: {AMAZON_URL}")
        driver.get(AMAZON_URL)
        time.sleep(3)

        # Set delivery location (pincode)
        try:
            # Click 'Deliver to' link/button
            deliver_to_elem = wait_for_element(driver, By.ID, "contextualIngressPtLabel")
            deliver_to_elem.click()
            time.sleep(1)
            # Enter pincode
            pincode_box = wait_for_element(driver, By.ID, "GLUXZipUpdateInput")
            pincode_box.clear()
            pincode_box.send_keys(AMAZON_PINCODE)
            apply_btn = driver.find_element(By.ID, "GLUXZipUpdate")
            apply_btn.click()
            time.sleep(2)
            # Wait for delivery update
            WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element((By.ID, "contextualIngressPtLabel"), AMAZON_PINCODE[:3])
            )
            logging.info(f"Delivery pincode set to {AMAZON_PINCODE}")
        except (TimeoutException, NoSuchElementException):
            logging.warning("Could not set delivery pincode (may already be set or UI changed).")

        # Add to cart
        try:
            add_to_cart_btn = wait_for_element(driver, By.ID, "add-to-cart-button")
            add_to_cart_btn.click()
            logging.info("Product added to cart.")
            time.sleep(2)
        except TimeoutException:
            logging.error("Add to Cart button not found. Product may be unavailable.")
            return

        # Proceed to cart/checkout
        try:
            # Sometimes a side-sheet opens, so we try both cart and proceed-to-checkout
            try:
                proceed_btn = wait_for_element(driver, By.ID, "hlb-ptc-btn-native", timeout=6)
                proceed_btn.click()
            except TimeoutException:
                # Try alternative button (sometimes 'proceed to checkout' is elsewhere)
                driver.get("https://www.amazon.in/gp/cart/view.html")
                proceed_btn2 = wait_for_element(driver, By.NAME, "proceedToRetailCheckout")
                proceed_btn2.click()
            logging.info("Proceeded to checkout.")
        except TimeoutException:
            logging.error("Proceed to checkout button not found.")
            return

        logging.info("Automation script completed purchase flow up to checkout page.")
        # Note: Payment/address steps are not automated for security/compliance reasons.
        print("SUCCESS: Purchase flow up to checkout completed.")

    except WebDriverException as e:
        logging.error(f"WebDriver error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        driver.quit()

# --- Usage Instructions ---
if __name__ == "__main__":
    """
    Usage:
    1. Set environment variables: AMAZON_USERNAME, AMAZON_PASSWORD, (optional) AMAZON_PINCODE, AMAZON_ASIN.
    2. Install dependencies: pip install selenium
    3. Download and install ChromeDriver.
    4. Run: python amazon_purchase.py
    5. Review logs for errors or success confirmation.
    """
    amazon_login_and_purchase()
