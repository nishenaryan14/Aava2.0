import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)

# --- CONFIGURATION ---
AMAZON_URL = "https://www.amazon.in/"
PRODUCT_ASIN = os.getenv("AMAZON_PRODUCT_ASIN", "B088N8G9RL")
PRODUCT_SEARCH_KEYWORD = os.getenv("AMAZON_PRODUCT_SEARCH", "Logitech wireless mouse")
AMAZON_USERNAME = os.getenv("AMAZON_USERNAME")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")
DELIVERY_PINCODE = os.getenv("AMAZON_PINCODE", "560001")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- LOGGING SETUP ---
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AmazonAutomation")

def wait_and_find(driver, by, value, timeout=15):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        logger.error(f"Timeout: Element '{value}' not found by {by}.")
        return None

def amazon_login(driver, username, password):
    logger.info("Navigating to Amazon login page.")
    driver.get(AMAZON_URL)
    sign_in_btn = wait_and_find(driver, By.ID, "nav-link-accountList")
    if not sign_in_btn:
        logger.error("Sign-in button not found.")
        return False
    sign_in_btn.click()

    email_input = wait_and_find(driver, By.ID, "ap_email")
    if not email_input:
        logger.error("Email input not found.")
        return False
    email_input.send_keys(username)
    driver.find_element(By.ID, "continue").click()

    password_input = wait_and_find(driver, By.ID, "ap_password")
    if not password_input:
        logger.error("Password input not found.")
        return False
    password_input.send_keys(password)
    driver.find_element(By.ID, "signInSubmit").click()

    # Check for login success or CAPTCHA
    time.sleep(3)
    if "authentication required" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
        logger.error("CAPTCHA detected or authentication required. Manual intervention needed.")
        return False
    if not driver.find_elements(By.ID, "nav-link-accountList-nav-line-1"):
        logger.error("Login failed. Please check credentials.")
        return False
    logger.info("Login successful.")
    return True

def search_and_select_product(driver, search_keyword, asin):
    logger.info(f"Searching for product: {search_keyword}")
    search_box = wait_and_find(driver, By.ID, "twotabsearchtextbox")
    if not search_box:
        logger.error("Search box not found.")
        return False
    search_box.clear()
    search_box.send_keys(search_keyword)
    search_box.send_keys(Keys.RETURN)

    # Wait for results to load
    time.sleep(2)
    logger.info(f"Locating product with ASIN: {asin}")
    try:
        product_link = driver.find_element(By.XPATH, f"//a[contains(@href,'{asin}')]")
        product_link.click()
    except NoSuchElementException:
        logger.error("Product with specified ASIN not found in search results.")
        return False
    logger.info("Product page opened.")
    return True

def set_delivery_pincode(driver, pincode):
    logger.info(f"Setting delivery pincode to: {pincode}")
    try:
        # Some product pages have a pincode input near "Deliver to"
        pincode_btn = wait_and_find(driver, By.ID, "contextualIngressPtLabel_deliveryShortLine")
        if pincode_btn:
            pincode_btn.click()
            pincode_input = wait_and_find(driver, By.ID, "GLUXZipUpdateInput")
            if pincode_input:
                pincode_input.clear()
                pincode_input.send_keys(pincode)
                driver.find_element(By.ID, "GLUXZipUpdate").click()
                time.sleep(2)
                logger.info("Delivery pincode set successfully.")
                return True
    except Exception as e:
        logger.warning(f"Could not set pincode automatically: {e}")
    logger.info("Proceeding without explicit pincode set (may default to account address).")
    return True

def add_to_cart_and_checkout(driver):
    logger.info("Adding product to cart.")
    add_cart_btn = wait_and_find(driver, By.ID, "add-to-cart-button")
    if not add_cart_btn:
        logger.error("Add to Cart button not found.")
        return False
    add_cart_btn.click()
    time.sleep(2)

    # Proceed to checkout
    try:
        proceed_btn = wait_and_find(driver, By.ID, "hlb-ptc-btn-native")
        if not proceed_btn:
            # Try alternate checkout button
            proceed_btn = wait_and_find(driver, By.NAME, "proceedToRetailCheckout")
        if proceed_btn:
            proceed_btn.click()
            logger.info("Proceeded to checkout page.")
            return True
        else:
            logger.error("Proceed to checkout button not found.")
            return False
    except Exception as e:
        logger.error(f"Error during checkout: {e}")
        return False

def main():
    # Validate input completeness
    if not (AMAZON_USERNAME and AMAZON_PASSWORD):
        logger.error("Missing Amazon credentials. Set AMAZON_USERNAME and AMAZON_PASSWORD as environment variables.")
        sys.exit(1)

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment for headless execution

    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as e:
        logger.error(f"WebDriver initialization failed: {e}")
        sys.exit(1)

    try:
        if not amazon_login(driver, AMAZON_USERNAME, AMAZON_PASSWORD):
            raise Exception("Login failed.")
        if not search_and_select_product(driver, PRODUCT_SEARCH_KEYWORD, PRODUCT_ASIN):
            raise Exception("Product selection failed.")
        if not set_delivery_pincode(driver, DELIVERY_PINCODE):
            logger.warning("Delivery pincode not set. Verify delivery address manually.")
        if not add_to_cart_and_checkout(driver):
            raise Exception("Add to cart or checkout failed.")

        logger.info("Amazon purchase automation completed successfully.")
    except Exception as e:
        logger.error(f"Automation failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
