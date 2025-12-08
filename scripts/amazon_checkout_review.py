import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

# --- CONFIGURATION ---
AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')
AMAZON_PRODUCT_ASIN = os.getenv('AMAZON_PRODUCT_ASIN', 'B088N8G9RL')
AMAZON_PINCODE = os.getenv('AMAZON_PINCODE', '560001')
AMAZON_BASE_URL = 'https://www.amazon.in/'

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

def wait_for_element(driver, by, value, timeout=15):
    """Wait for element to appear, return element or raise TimeoutException."""
    for _ in range(timeout):
        try:
            elem = driver.find_element(by, value)
            return elem
        except NoSuchElementException:
            time.sleep(1)
    raise TimeoutException(f"Element {value} not found after {timeout}s")

def amazon_login(driver, username, password):
    logging.info('Navigating to Amazon login page...')
    driver.get(AMAZON_BASE_URL)
    # Click login
    wait_for_element(driver, By.ID, 'nav-link-accountList').click()
    wait_for_element(driver, By.ID, 'ap_email').send_keys(username)
    wait_for_element(driver, By.ID, 'continue').click()
    wait_for_element(driver, By.ID, 'ap_password').send_keys(password)
    wait_for_element(driver, By.ID, 'signInSubmit').click()
    # Check for login success
    time.sleep(2)
    if "authentication" in driver.current_url or "signin" in driver.current_url:
        raise Exception("Amazon login failed. Check credentials or CAPTCHA.")

def navigate_to_product(driver, asin):
    product_url = f"{AMAZON_BASE_URL}dp/{asin}"
    logging.info(f'Navigating to product: {product_url}')
    driver.get(product_url)
    time.sleep(2)
    # Verify product page loaded
    try:
        product_title = wait_for_element(driver, By.ID, 'productTitle', timeout=10).text
        logging.info(f'Product page loaded: {product_title}')
    except TimeoutException:
        raise Exception("Product page failed to load.")

def set_delivery_pincode(driver, pincode):
    logging.info(f'Setting delivery pincode: {pincode}')
    try:
        # Click 'Deliver to' (pincode popup)
        deliver_elem = wait_for_element(driver, By.ID, 'contextualIngressPtLabel', timeout=10)
        deliver_elem.click()
        # Wait and enter pincode
        time.sleep(2)
        input_elem = wait_for_element(driver, By.ID, 'GLUXZipUpdateInput', timeout=10)
        input_elem.clear()
        input_elem.send_keys(pincode)
        wait_for_element(driver, By.ID, 'GLUXZipUpdate').click()
        time.sleep(3)
        logging.info('Pincode set successfully.')
    except Exception as e:
        logging.warning(f'Pincode selection failed: {e}')

def add_to_cart(driver):
    logging.info('Adding product to cart...')
    try:
        add_btn = wait_for_element(driver, By.ID, 'add-to-cart-button', timeout=10)
        add_btn.click()
        time.sleep(2)
        # Close protection plan popup if exists
        try:
            no_thanks_btn = driver.find_element(By.XPATH, "//button[contains(.,'No Thanks')]")
            no_thanks_btn.click()
            time.sleep(1)
        except NoSuchElementException:
            pass
        logging.info('Product added to cart.')
    except TimeoutException:
        raise Exception("Add to cart button not found.")

def proceed_to_checkout_review(driver):
    logging.info('Proceeding to checkout review...')
    try:
        # Go to cart
        driver.get(f"{AMAZON_BASE_URL}gp/cart/view.html")
        time.sleep(2)
        # Proceed to checkout
        checkout_btn = wait_for_element(driver, By.NAME, 'proceedToRetailCheckout', timeout=10)
        checkout_btn.click()
        time.sleep(5)
        # At checkout review: do NOT place order!
        # Extract review details
        try:
            summary = driver.find_element(By.ID, 'subtotals-marketplace-table').text
            logging.info(f'Checkout Summary:\n{summary}')
        except NoSuchElementException:
            logging.info('Checkout summary not found, verify manually.')
        logging.info('Reached checkout review (no order placed).')
    except Exception as e:
        raise Exception(f"Checkout review failed: {e}")

def main():
    if not all([AMAZON_USERNAME, AMAZON_PASSWORD]):
        logging.error('Amazon credentials missing. Set AMAZON_USERNAME and AMAZON_PASSWORD as environment variables.')
        return
    driver = webdriver.Chrome()
    try:
        amazon_login(driver, AMAZON_USERNAME, AMAZON_PASSWORD)
        navigate_to_product(driver, AMAZON_PRODUCT_ASIN)
        set_delivery_pincode(driver, AMAZON_PINCODE)
        add_to_cart(driver)
        proceed_to_checkout_review(driver)
        logging.info('Automation flow completed successfully.')
    except Exception as e:
        logging.error(f'Automation error: {e}')
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
