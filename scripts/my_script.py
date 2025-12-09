# Selenium Automation Script for Flipkart: Login, Search, and Add HP Mouse to Cart

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# --- CONFIGURATION ---
FLIPKART_URL = 'https://www.flipkart.com/'
USERNAME = 'your_email_or_phone'
PASSWORD = 'your_password'
SEARCH_TERM = 'hp mouse'

# --- SCRIPT START ---
def main():
    driver = webdriver.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    try:
        # Step 1: Go to Flipkart
        driver.get(FLIPKART_URL)
        assert 'Flipkart' in driver.title, 'Flipkart homepage did not load.'
        print('Opened Flipkart homepage.')

        # Step 2: Close login popup if present
        try:
            close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"✕")]')))
            close_btn.click()
            print('Closed initial login popup.')
        except TimeoutException:
            print('Login popup not found, proceeding.')

        # Step 3: Click Login
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(),"Login")]')))
        login_btn.click()
        print('Clicked Login button.')

        # Step 4: Enter credentials
        username_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@class="_2IX_2- VJZDxU"]')))
        password_input = driver.find_element(By.XPATH, '//input[@type="password"]')
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        print('Entered credentials.')

        # Step 5: Submit login
        submit_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
        submit_btn.click()
        print('Submitted login form.')
        time.sleep(3)

        # Step 6: Assert login success
        try:
            account_icon = wait.until(EC.presence_of_element_located((By.XPATH, '//div[text()="My Account"]')))
            assert account_icon.is_displayed(), 'Login failed or My Account not visible.'
            print('Login successful.')
        except TimeoutException:
            print('Login may have failed. Check credentials.')
            driver.quit()
            return

        # Step 7: Search for HP Mouse
        search_box = wait.until(EC.presence_of_element_located((By.NAME, 'q')))
        search_box.clear()
        search_box.send_keys(SEARCH_TERM)
        search_box.send_keys(Keys.RETURN)
        print(f'Searched for {SEARCH_TERM}.')

        # Step 8: Wait for results and select first product
        product_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"_4rR01T") or contains(@class,"s1Q9rs")]')))
        product_name = product_link.text
        product_link.click()
        print(f'Selected product: {product_name}')

        # Step 9: Switch to new tab
        driver.switch_to.window(driver.window_handles[-1])

        # Step 10: Add to cart
        add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Add to cart")]')))
        add_to_cart_btn.click()
        print('Clicked Add to Cart.')
        time.sleep(2)

        # Step 11: Assert item added to cart
        cart_count = wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(@class,"_2YsvKq")]')))
        assert int(cart_count.text) > 0, 'Cart count did not increase.'
        print('HP Mouse added to cart successfully.')

    except (TimeoutException, NoSuchElementException, AssertionError) as e:
        print(f'Error occurred: {e}')
    finally:
        driver.quit()
        print('Browser closed.')

if __name__ == "__main__":
    main()
