from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def get_driver(browser='chrome'):
    """
    Initializes and returns a Selenium WebDriver instance.
    Args:
        browser (str): Browser type ('chrome' or 'firefox')
    Returns:
        driver (WebDriver): Selenium WebDriver instance
    """
    if browser.lower() == 'chrome':
        return webdriver.Chrome()
    elif browser.lower() == 'firefox':
        return webdriver.Firefox()
    else:
        raise ValueError('Unsupported browser type: {}'.format(browser))

def login_amazon(driver, username, password):
    """
    Logs into Amazon using provided credentials.
    Args:
        driver (WebDriver): Selenium WebDriver instance
        username (str): Amazon username/email
        password (str): Amazon password
    Returns:
        bool: True if login was successful, False otherwise
    """
    try:
        driver.get('https://www.amazon.com/')
        sign_in_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'nav-link-accountList'))
        )
        sign_in_btn.click()

        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'ap_email'))
        )
        email_field.send_keys(username)
        driver.find_element(By.ID, 'continue').click()

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'ap_password'))
        )
        password_field.send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()

        # Validate login by checking for account name or account list
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'nav-link-accountList'))
        )
        return True
    except Exception as e:
        print(f'Login failed: {e}')
        return False

def search_and_add_to_cart(driver, search_term):
    """
    Searches for a product and adds the first result to cart.
    Args:
        driver (WebDriver): Selenium WebDriver instance
        search_term (str): Product search query
    Returns:
        bool: True if product added to cart, False otherwise
    """
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'twotabsearchtextbox'))
        )
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results and click first result
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.s-main-slot div[data-component-type="s-search-result"] h2 a'))
        )
        first_result.click()

        # Switch to new tab if product opens in a new tab
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])

        add_to_cart_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'add-to-cart-button'))
        )
        add_to_cart_btn.click()

        # Validate addition to cart
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'nav-cart-count'))
        )
        cart_count = driver.find_element(By.ID, 'nav-cart-count').text
        assert int(cart_count) >= 1, "Cart count did not increment."
        return True
    except Exception as e:
        print(f'Failed to add product to cart: {e}')
        return False

def main(username, password, search_term, browser='chrome'):
    """
    Main test flow: login, search, add to cart.
    Args:
        username (str): Amazon username/email
        password (str): Amazon password
        search_term (str): Product search query
        browser (str): Browser type
    """
    driver = get_driver(browser)
    driver.maximize_window()
    try:
        login_success = login_amazon(driver, username, password)
        assert login_success, "Login step failed."

        add_to_cart_success = search_and_add_to_cart(driver, search_term)
        assert add_to_cart_success, "Add to cart step failed."

        print("Test completed successfully: Product added to cart.")
    except AssertionError as ae:
        print(f'Test assertion failed: {ae}')
    except Exception as e:
        print(f'Unexpected error: {e}')
    finally:
        driver.quit()

if __name__ == '__main__':
    # Credentials can be parameterized or loaded from environment variables for security
    USERNAME = os.getenv('AMAZON_USERNAME', 'demo_user')
    PASSWORD = os.getenv('AMAZON_PASSWORD', 'demo_pass')
    SEARCH_TERM = 'HP mouse'
    BROWSER = os.getenv('SELENIUM_BROWSER', 'chrome')
    main(USERNAME, PASSWORD, SEARCH_TERM, BROWSER)
