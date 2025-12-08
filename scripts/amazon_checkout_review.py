import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException
)
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    filename='amazon_purchase.log', level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def amazon_login_and_purchase_review(
    username, password, asin, pincode, headless=True
):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    try:
        logging.info("Navigating to Amazon home page.")
        driver.get('https://www.amazon.in/')
        time.sleep(2)

        # Login
        logging.info("Attempting login.")
        driver.find_element(By.ID, 'nav-link-accountList').click()
        driver.find_element(By.ID, 'ap_email').send_keys(username)
        driver.find_element(By.ID, 'continue').click()
        driver.find_element(By.ID, 'ap_password').send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()
        time.sleep(2)

        # Check for login errors
        if "authentication" in driver.current_url or "ap/signin" in driver.current_url:
            raise Exception("Login failed. Check credentials or CAPTCHA challenge.")

        # Navigate to product page via ASIN
        product_url = f"https://www.amazon.in/dp/{asin}"
        logging.info(f"Navigating to product page: {product_url}")
        driver.get(product_url)
        time.sleep(2)

        # Set delivery pincode
        try:
            logging.info(f"Setting delivery pincode: {pincode}")
            # Find location/pincode input (varies by UI version)
            try:
                driver.find_element(By.ID, 'contextualIngressPtLabel').click()
            except NoSuchElementException:
                pass  # Already open or not required

            time.sleep(1)
            pincode_input = driver.find_element(By.ID, 'GLUXZipUpdateInput')
            pincode_input.clear()
            pincode_input.send_keys(pincode)
            driver.find_element(By.ID, 'GLUXZipUpdate').click()
            time.sleep(2)
            # Wait for delivery update (may reload page)
        except NoSuchElementException:
            logging.warning("Pincode input not found; skipping pincode set.")

        # Add to cart
        try:
            logging.info("Adding product to cart.")
            add_to_cart_btn = driver.find_element(By.ID, 'add-to-cart-button')
            add_to_cart_btn.click()
            time.sleep(2)
        except NoSuchElementException:
            raise Exception("Add to cart button not found. Product may be out of stock or unavailable.")

        # Proceed to cart/checkout
        try:
            logging.info("Proceeding to cart/checkout review.")
            # Sometimes a side sheet appears; try to find 'Proceed to Buy'
            try:
                driver.find_element(By.ID, 'attach-sidesheet-view-cart-button').click()
                time.sleep(2)
            except NoSuchElementException:
                pass  # No side sheet

            # Go to cart if not redirected
            if "cart" not in driver.current_url:
                driver.get("https://www.amazon.in/gp/cart/view.html")
                time.sleep(2)

            # Proceed to checkout review
            driver.find_element(By.NAME, 'proceedToRetailCheckout').click()
            time.sleep(3)
        except NoSuchElementException:
            raise Exception("Proceed to checkout button not found.")

        # At checkout review: Extract price, delivery, and payment options
        logging.info("Extracting checkout review information.")
        # Price
        try:
            price_elem = driver.find_element(By.XPATH, "//span[contains(@class,'grand-total-price')]")
            price = price_elem.text
        except NoSuchElementException:
            price = "N/A"

        # Delivery option
        try:
            delivery_elem = driver.find_element(By.XPATH, "//span[contains(@class,'delivery-message')]")
            delivery = delivery_elem.text
        except NoSuchElementException:
            delivery = "N/A"

        # Payment methods (list available)
        try:
            payment_methods = []
            payment_elems = driver.find_elements(By.XPATH, "//div[contains(@class,'pmts-instrument-list')]//span")
            for el in payment_elems:
                payment_methods.append(el.text)
        except NoSuchElementException:
            payment_methods = ["N/A"]

        print("=== Checkout Review ===")
        print(f"Price: {price}")
        print(f"Delivery: {delivery}")
        print(f"Payment methods: {payment_methods}")

        logging.info(f"Checkout Review - Price: {price}, Delivery: {delivery}, Payment Methods: {payment_methods}")

    except Exception as e:
        logging.error(f"Error during automation: {e}")
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    # Load credentials and parameters from environment variables
    username = os.getenv('AMAZON_USERNAME')
    password = os.getenv('AMAZON_PASSWORD')
    asin = os.getenv('AMAZON_ASIN', 'B088N8G9RL')  # Default to Logitech mouse
    pincode = os.getenv('AMAZON_PINCODE', '560001')
    headless = os.getenv('HEADLESS', 'True').lower() == 'true'

    if not all([username, password, asin, pincode]):
        print("Error: Missing required environment variables. Please set AMAZON_USERNAME, AMAZON_PASSWORD, AMAZON_ASIN, AMAZON_PINCODE.")
    else:
        amazon_login_and_purchase_review(username, password, asin, pincode, headless=headless)
