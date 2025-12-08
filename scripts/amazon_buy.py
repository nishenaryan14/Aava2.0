import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

# --- Configuration ---
AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')
AMAZON_ASIN = os.getenv('AMAZON_ASIN', 'B088N8G9RL')
AMAZON_PINCODE = os.getenv('AMAZON_PINCODE', '560001')
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', 'chromedriver')  # Adjust path as needed

# --- Helper Functions ---
def log(msg):
    print(f"[AmazonAutomation] {msg}")

def wait_for_element(driver, by, value, timeout=10):
    for i in range(timeout):
        try:
            elem = driver.find_element(by, value)
            return elem
        except NoSuchElementException:
            time.sleep(1)
    raise TimeoutException(f"Element not found: {value}")

# --- Main Automation ---
def amazon_login_and_buy(username, password, asin, pincode):
    # Configure browser options for headless execution if desired
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode

    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)
    driver.implicitly_wait(10)
    try:
        log("Navigating to Amazon homepage...")
        driver.get('https://www.amazon.in/')  # Adjust domain as needed

        log("Clicking 'Sign In'...")
        sign_in = wait_for_element(driver, By.ID, 'nav-link-accountList')
        sign_in.click()

        log("Entering username...")
        email_input = wait_for_element(driver, By.ID, 'ap_email')
        email_input.send_keys(username)
        driver.find_element(By.ID, 'continue').click()

        log("Entering password...")
        password_input = wait_for_element(driver, By.ID, 'ap_password')
        password_input.send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()
        time.sleep(2)

        # Check for login failure or CAPTCHA
        if "authentication required" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
            log("Login failed or CAPTCHA detected. Exiting.")
            return

        log(f"Searching for product ASIN: {asin}...")
        driver.get(f"https://www.amazon.in/dp/{asin}")

        # Set delivery pincode
        try:
            log(f"Setting delivery to pincode {pincode}...")
            deliver_to = wait_for_element(driver, By.ID, 'contextualIngressPtLabel')
            deliver_to.click()
            pincode_input = wait_for_element(driver, By.ID, 'GLUXZipUpdateInput')
            pincode_input.clear()
            pincode_input.send_keys(pincode)
            driver.find_element(By.ID, 'GLUXZipUpdate').click()
            time.sleep(3)
        except Exception as e:
            log(f"Could not set pincode: {e}")

        # Add to cart
        log("Adding product to cart...")
        add_to_cart = wait_for_element(driver, By.ID, 'add-to-cart-button')
        add_to_cart.click()
        time.sleep(2)

        # Go to cart and proceed to checkout
        log("Proceeding to checkout...")
        try:
            proceed_to_checkout = wait_for_element(driver, By.ID, 'hlb-ptc-btn-native')
            proceed_to_checkout.click()
        except Exception:
            # Alternate checkout button
            try:
                proceed_to_checkout_alt = wait_for_element(driver, By.NAME, 'proceedToRetailCheckout')
                proceed_to_checkout_alt.click()
            except Exception as e:
                log(f"Checkout button not found: {e}")
                return

        # At this point, address/payment selection would be required.
        log("Purchase flow completed up to checkout page. Manual intervention required for payment/address selection.")
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        log(f"Error during automation: {e}")
    finally:
        driver.quit()
        log("Browser closed.")

# --- Usage Example ---
if __name__ == '__main__':
    if not AMAZON_USERNAME or not AMAZON_PASSWORD:
        log("Error: AMAZON_USERNAME and AMAZON_PASSWORD environment variables must be set.")
    else:
        amazon_login_and_buy(AMAZON_USERNAME, AMAZON_PASSWORD, AMAZON_ASIN, AMAZON_PINCODE)

"""
# Setup Guide:
1. Install Python 3.x and pip.
2. Install Selenium: pip install selenium
3. Download ChromeDriver and add to PATH or specify location in CHROME_DRIVER_PATH.
4. Set environment variables:
   export AMAZON_USERNAME='your_amazon_email'
   export AMAZON_PASSWORD='your_amazon_password'
   export AMAZON_ASIN='B088N8G9RL'
   export AMAZON_PINCODE='560001'
5. Run the script: python amazon_buy.py

# Usage Notes:
- Script automates login, product selection, pincode delivery, cart addition, and checkout navigation.
- Payment and address selection steps require manual intervention for security.
- All credentials and sensitive info are handled via environment variables.
- For troubleshooting, review printed logs and check for UI changes.

# Maintenance:
- Update element selectors if Amazon UI changes.
- Rotate credentials regularly.
- Monitor for anti-bot or CAPTCHA triggers.

# Troubleshooting:
- If login fails, check credentials and network.
- If product not found, verify ASIN.
- If CAPTCHA appears, script cannot proceed automatically.

# Enhancement:
- Extend for multiple products.
- Integrate with CI/CD for automated runs.
- Implement advanced error reporting/logging.
"""
