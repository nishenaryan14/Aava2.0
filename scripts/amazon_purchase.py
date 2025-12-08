import os
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

# =============================== CONFIGURATION ===============================
# Credentials and product details are read from environment variables for security
AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')
AMAZON_ASIN = os.getenv('AMAZON_ASIN', 'B088N8G9RL')  # Logitech wireless mouse default
AMAZON_PINCODE = os.getenv('AMAZON_PINCODE', '560001')
AMAZON_BASE_URL = 'https://www.amazon.in/'  # Use .com for US, .in for India

# =============================== MAIN FUNCTION ===============================
def amazon_login_and_buy(username, password, asin, pincode, headless=False):
    """
    Automates Amazon login, product selection (by ASIN), delivery pincode setting,
    cart addition, and checkout initiation.
    Args:
        username (str): Amazon login email/username
        password (str): Amazon account password
        asin (str): Amazon Standard Identification Number for the product
        pincode (str): Delivery location pincode
        headless (bool): Run browser in headless mode
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    log_messages = []

    try:
        # Step 1: Navigate to Amazon homepage
        driver.get(AMAZON_BASE_URL)
        log_messages.append("Navigated to Amazon homepage.")

        # Step 2: Click 'Sign In'
        sign_in = wait.until(EC.element_to_be_clickable((By.ID, 'nav-link-accountList')))
        sign_in.click()
        log_messages.append("Clicked Sign In.")

        # Step 3: Enter username and continue
        email_input = wait.until(EC.presence_of_element_located((By.ID, 'ap_email')))
        email_input.clear()
        email_input.send_keys(username)
        driver.find_element(By.ID, 'continue').click()
        log_messages.append("Entered username.")

        # Step 4: Enter password and login
        password_input = wait.until(EC.presence_of_element_located((By.ID, 'ap_password')))
        password_input.clear()
        password_input.send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()
        log_messages.append("Entered password and logged in.")

        # Step 5: Search for product by ASIN
        search_box = wait.until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
        search_box.clear()
        search_box.send_keys(asin)
        search_box.send_keys(Keys.RETURN)
        log_messages.append(f"Searched for product ASIN {asin}.")

        # Step 6: Click on the product link matching ASIN
        product_link_xpath = f"//a[contains(@href, '/dp/{asin}')]
        product_link = wait.until(EC.element_to_be_clickable((By.XPATH, product_link_xpath)))
        product_link.click()
        log_messages.append(f"Opened product page for ASIN {asin}.")

        # Step 7: Set delivery pincode
        try:
            # Different UI elements for pincode depending on login state/location
            pincode_button = wait.until(EC.element_to_be_clickable((By.ID, 'contextualIngressPtLabel')))
            pincode_button.click()
            log_messages.append("Clicked pincode change link.")
            pincode_input = wait.until(EC.presence_of_element_located((By.ID, 'GLUXZipUpdateInput')))
            pincode_input.clear()
            pincode_input.send_keys(pincode)
            driver.find_element(By.ID, 'GLUXZipUpdate').click()
            log_messages.append(f"Set delivery pincode to {pincode}.")
            # Wait for pincode to update delivery message
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            log_messages.append("Pincode change UI not found, skipping step.")

        # Step 8: Add product to cart
        add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.ID, 'add-to-cart-button')))
        add_to_cart_btn.click()
        log_messages.append("Added product to cart.")

        # Step 9: Proceed to checkout
        try:
            proceed_btn = wait.until(EC.element_to_be_clickable((By.ID, 'hlb-ptc-btn-native')))
            proceed_btn.click()
            log_messages.append("Proceeded to checkout.")
        except (NoSuchElementException, TimeoutException):
            log_messages.append("Proceed to checkout button not found. Possibly redirected to cart.")
            driver.get(f"{AMAZON_BASE_URL}gp/cart/view.html")
            checkout_btn = wait.until(EC.element_to_be_clickable((By.NAME, 'proceedToRetailCheckout')))
            checkout_btn.click()
            log_messages.append("Proceeded to checkout from cart page.")

        print("Purchase flow completed successfully.")
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        print(f"Error during automation: {e}")
        log_messages.append(f"Error: {e}")
    finally:
        # Log all steps for troubleshooting
        for msg in log_messages:
            print(msg)
        driver.quit()

# =============================== USAGE EXAMPLE ===============================
if __name__ == '__main__':
    if not AMAZON_USERNAME or not AMAZON_PASSWORD:
        print("ERROR: Please set AMAZON_USERNAME and AMAZON_PASSWORD as environment variables.")
    else:
        amazon_login_and_buy(
            username=AMAZON_USERNAME,
            password=AMAZON_PASSWORD,
            asin=AMAZON_ASIN,
            pincode=AMAZON_PINCODE,
            headless=False  # Set to True for headless execution
        )
