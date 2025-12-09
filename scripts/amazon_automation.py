from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class AmazonAutomation:
    """
    Automates the process of logging in to Amazon, searching for an HP mouse, and adding it to the cart.
    """

    def __init__(self, username, password, browser='chrome', base_url='https://www.amazon.com'):
        """
        Initializes the AmazonAutomation class with user credentials and browser selection.
        Args:
            username (str): Amazon username
            password (str): Amazon password
            browser (str): Browser type ('chrome' or 'firefox')
            base_url (str): Amazon base URL
        """
        self.username = username
        self.password = password
        self.base_url = base_url
        self.driver = self._init_driver(browser)

    def _init_driver(self, browser):
        """
        Initializes the Selenium WebDriver.
        """
        if browser.lower() == 'chrome':
            return webdriver.Chrome()
        elif browser.lower() == 'firefox':
            return webdriver.Firefox()
        else:
            raise ValueError("Unsupported browser: choose 'chrome' or 'firefox'")

    def login(self):
        """
        Logs in to Amazon using the provided credentials.
        """
        driver = self.driver
        driver.get(self.base_url)
        try:
            # Click 'Sign in' button
            sign_in_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "nav-link-accountList"))
            )
            sign_in_btn.click()

            # Enter username
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ap_email"))
            )
            email_input.clear()
            email_input.send_keys(self.username)
            driver.find_element(By.ID, "continue").click()

            # Enter password
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ap_password"))
            )
            password_input.clear()
            password_input.send_keys(self.password)
            driver.find_element(By.ID, "signInSubmit").click()

            # Verify login by checking for "Accounts & Lists"
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "nav-link-accountList"))
            )
            print("Login successful.")
        except Exception as e:
            print(f"Login failed: {e}")
            driver.save_screenshot("login_error.png")
            raise

    def search_product(self, product_name):
        """
        Searches for a product on Amazon.
        Args:
            product_name (str): Name of the product to search
        """
        driver = self.driver
        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
            )
            search_box.clear()
            search_box.send_keys(product_name)
            search_box.send_keys(Keys.RETURN)

            # Wait for search results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
            )
            print(f"Search for '{product_name}' successful.")
        except Exception as e:
            print(f"Search failed: {e}")
            driver.save_screenshot("search_error.png")
            raise

    def add_first_product_to_cart(self):
        """
        Adds the first listed HP mouse to the cart.
        """
        driver = self.driver
        try:
            # Find first product in results
            products = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']"))
            )
            if not products:
                raise Exception("No products found in search results.")

            # Click the first product
            products[0].find_element(By.CSS_SELECTOR, "h2 a").click()

            # Switch to new tab if opened
            driver.switch_to.window(driver.window_handles[-1])

            # Wait for 'Add to Cart' button
            add_to_cart_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
            )
            add_to_cart_btn.click()

            # Confirm item added to cart
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "nav-cart-count"))
            )
            cart_count = driver.find_element(By.ID, "nav-cart-count").text
            assert int(cart_count) > 0, "Cart count did not increase."
            print("Product added to cart successfully.")
        except Exception as e:
            print(f"Add to cart failed: {e}")
            driver.save_screenshot("add_to_cart_error.png")
            raise

    def teardown(self):
        """
        Closes the browser and cleans up.
        """
        self.driver.quit()

def main():
    # Use environment variables for credentials in production
    username = os.getenv('AMAZON_USERNAME', 'demo_user')
    password = os.getenv('AMAZON_PASSWORD', 'demo_pass')
    browser = os.getenv('SELENIUM_BROWSER', 'chrome')

    amazon = AmazonAutomation(username, password, browser)
    try:
        amazon.login()
        amazon.search_product("HP mouse")
        amazon.add_first_product_to_cart()
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        amazon.teardown()

if __name__ == "__main__":
    main()
