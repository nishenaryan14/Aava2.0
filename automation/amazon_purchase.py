import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)

# -----------------------------
# Configuration
# -----------------------------
AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')
AMAZON_PINCODE = os.getenv('AMAZON_PINCODE', '560001')
PRODUCT_ASIN = os.getenv('AMAZON_PRODUCT_ASIN', 'B088N8G9RL')
PRODUCT_URL = f"https://www.amazon.in/dp/{PRODUCT_ASIN}"

if not AMAZON_USERNAME or not AMAZON_PASSWORD:
    print("ERROR: Please set AMAZON_USERNAME and AMAZON_PASSWORD environment variables.")
    sys.exit(1)

# -----------------------------
# Main Automation Function
# -----------------------------
def amazon_login_and_purchase():
    # Initialize WebDriver (Chrome)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Uncomment for headless execution:
    # options.add_argument("--headless")
    try:
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        driver.get("https://www.amazon.in/")

        # Click 'Sign In'
        wait.until(EC.element_to_be_clickable((By.ID, "nav-link-accountList"))).click()

        # Enter Username
        wait.until(EC.visibility_of_element_located((By.ID, "ap_email"))).send_keys(AMAZON_USERNAME)
        driver.find_element(By.ID, "continue").click()

        # Enter Password
        wait.until(EC.visibility_of_element_located((By.ID, "ap_password"))).send_keys(AMAZON_PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()

        # Check for CAPTCHA (manual intervention required)
        if "authentication/captcha" in driver.current_url:
            print("CAPTCHA encountered. Manual intervention required.")
            driver.quit()
            return

        # Navigate directly to product URL
        driver.get(PRODUCT_URL)

        # Validate product page loaded
        try:
            product_title = wait.until(EC.presence_of_element_located((By.ID, "productTitle"))).text
            print(f"Product page loaded: {product_title}")
        except TimeoutException:
            print("ERROR: Product page did not load. Check ASIN or network.")
            driver.quit()
            return

        # Set delivery pincode
        try:
            # Click 'Deliver to' (if not already set)
            deliver_to = wait.until(EC.element_to_be_clickable((By.ID, "contextualIngressPtLabel")))
            deliver_to.click()
            pincode_input = wait.until(EC.visibility_of_element_located((By.ID, "GLUXZipUpdateInput")))
            pincode_input.clear()
            pincode_input.send_keys(AMAZON_PINCODE)
            driver.find_element(By.ID, "GLUXZipUpdate").click()
            # Wait for delivery option to refresh
            time.sleep(3)
            print(f"Delivery pincode set to {AMAZON_PINCODE}")
        except (NoSuchElementException, TimeoutException):
            print("WARNING: Could not set delivery pincode. It may already be set.")

        # Add 1 unit to cart
        try:
            add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-button")))
            add_to_cart_btn.click()
            print("Product added to cart.")
        except (NoSuchElementException, TimeoutException):
            print("ERROR: Add to cart button not found.")
            driver.quit()
            return

        # Proceed to cart/checkout
        try:
            # Wait for cart confirmation
            time.sleep(2)
            proceed_btn = None
            # Try native proceed to checkout
            try:
                proceed_btn = driver.find_element(By.ID, "hlb-ptc-btn-native")
            except NoSuchElementException:
                # Try alternate checkout button
                try:
                    proceed_btn = driver.find_element(By.NAME, "proceedToRetailCheckout")
                except NoSuchElementException:
                    pass
            if proceed_btn:
                proceed_btn.click()
                print("Proceeded to checkout.")
            else:
                print("WARNING: Proceed to checkout button not found. Please check cart manually.")
        except Exception as e:
            print(f"ERROR during checkout navigation: {e}")

        # NOTE: Address selection, payment automation is not included for security/compliance.
        print("Automation flow completed successfully. Please review cart and complete payment manually.")

    except WebDriverException as e:
        print(f"WebDriver error: {e}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")
    finally:
        driver.quit()

# -----------------------------
# Usage Example
# -----------------------------
if __name__ == "__main__":
    """
    Usage Instructions:
    1. Set AMAZON_USERNAME, AMAZON_PASSWORD, and optionally AMAZON_PINCODE, AMAZON_PRODUCT_ASIN as environment variables.
    2. Ensure ChromeDriver is installed and on PATH.
    3. Run: python amazon_purchase.py
    4. Follow console/log output. If CAPTCHA is encountered, manual intervention may be needed.
    5. For troubleshooting, review error messages and update selectors if Amazon UI changes.
    """
    amazon_login_and_purchase()
