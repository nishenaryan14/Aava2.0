from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def amazon_login_and_add_to_cart(
    username='demo_user',
    password='demo_pass',
    product_search='HP mouse',
    browser='chrome',
    base_url='https://www.amazon.com'
):
    """
    Automates Amazon login, product search, and add-to-cart functionality.
    Args:
        username (str): Amazon username/email.
        password (str): Amazon password.
        product_search (str): Product to search for.
        browser (str): Browser type ('chrome' or 'firefox').
        base_url (str): Amazon website URL.
    """
    # Initialize WebDriver
    if browser.lower() == 'chrome':
        driver = webdriver.Chrome()
    elif browser.lower() == 'firefox':
        driver = webdriver.Firefox()
    else:
        raise ValueError('Unsupported browser: {}'.format(browser))

    wait = WebDriverWait(driver, 20)
    try:
        # Step 1: Open Amazon homepage
        driver.get(base_url)
        driver.maximize_window()

        # Step 2: Click 'Sign In'
        sign_in_elem = wait.until(EC.element_to_be_clickable((By.ID, 'nav-link-accountList')))
        sign_in_elem.click()

        # Step 3: Enter username/email
        email_field = wait.until(EC.presence_of_element_located((By.ID, 'ap_email')))
        email_field.clear()
        email_field.send_keys(username)
        driver.find_element(By.ID, 'continue').click()

        # Step 4: Enter password
        password_field = wait.until(EC.presence_of_element_located((By.ID, 'ap_password')))
        password_field.clear()
        password_field.send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()

        # Step 5: Assert login success (e.g., check for account link)
        wait.until(EC.presence_of_element_located((By.ID, 'nav-link-accountList')))
        assert 'Amazon.com' in driver.title, "Login may have failed or page did not load as expected."

        # Step 6: Search for the product
        search_box = wait.until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
        search_box.clear()
        search_box.send_keys(product_search)
        search_box.send_keys(Keys.RETURN)

        # Step 7: Assert search results are displayed
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.s-main-slot')))
        assert product_search.lower() in driver.page_source.lower(), "Search results do not contain the product."

        # Step 8: Click the first product link
        product_links = driver.find_elements(By.CSS_SELECTOR, 'div.s-main-slot div[data-component-type="s-search-result"] h2 a')
        if not product_links:
            raise Exception("No products found for search: {}".format(product_search))
        product_links[0].click()

        # Step 9: Switch to product tab if opened
        driver.switch_to.window(driver.window_handles[-1])

        # Step 10: Add product to cart
        add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.ID, 'add-to-cart-button')))
        add_to_cart_btn.click()

        # Step 11: Assert product added to cart (look for confirmation)
        cart_confirmation = wait.until(
            EC.presence_of_element_located((By.XPATH, '//h1[contains(text(),"Added to Cart")]'))
        )
        assert cart_confirmation.is_displayed(), "Add to cart confirmation not displayed."

        print("Test Passed: Login, search, and add to cart succeeded.")

    except Exception as e:
        print(f"Test Failed: {e}")
    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    # For production, use environment variables for credentials
    amazon_login_and_add_to_cart(
        username=os.getenv('AMAZON_USERNAME', 'demo_user'),
        password=os.getenv('AMAZON_PASSWORD', 'demo_pass'),
        product_search='HP mouse',
        browser=os.getenv('BROWSER', 'chrome')
    )
