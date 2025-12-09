# Selenium Automation Script for Amazon: Login, Search, and Add to Cart

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# --- Configuration ---
AMAZON_URL = 'https://www.amazon.com/'
USERNAME = 'your_amazon_email@example.com'  # Replace with your Amazon email
PASSWORD = 'your_amazon_password'            # Replace with your Amazon password
SEARCH_TERM = 'hp mouse'

# --- WebDriver Setup ---
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

try:
    # Step 1: Visit Amazon
    driver.get(AMAZON_URL)
    assert 'Amazon' in driver.title, 'Amazon homepage did not load.'
    print('Amazon homepage loaded.')

    # Step 2: Click on Sign In
    sign_in_btn = wait.until(EC.element_to_be_clickable((By.ID, 'nav-link-accountList')))
    sign_in_btn.click()
    print('Navigated to Sign-In page.')

    # Step 3: Enter Username
    email_input = wait.until(EC.presence_of_element_located((By.ID, 'ap_email')))
    email_input.send_keys(USERNAME)
    driver.find_element(By.ID, 'continue').click()
    print('Entered email and continued.')

    # Step 4: Enter Password
    password_input = wait.until(EC.presence_of_element_located((By.ID, 'ap_password')))
    password_input.send_keys(PASSWORD)
    driver.find_element(By.ID, 'signInSubmit').click()
    print('Entered password and signed in.')

    # Assertion: Check login success
    try:
        account_text = wait.until(EC.presence_of_element_located((By.ID, 'nav-link-accountList-nav-line-1')))
        assert USERNAME.split('@')[0] in account_text.text, 'Login validation failed.'
        print('Login successful.')
    except TimeoutException:
        raise Exception('Login failed or took too long.')

    # Step 5: Search for HP Mouse
    search_box = wait.until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
    search_box.clear()
    search_box.send_keys(SEARCH_TERM)
    search_box.send_keys(Keys.RETURN)
    print(f'Searched for {SEARCH_TERM}.')

    # Assertion: Check search results
    wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'results for')]")) )
    print('Search results page loaded.')

    # Step 6: Click on the first HP Mouse product
    product_link = None
    try:
        product_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'HP') and contains(text(), 'Mouse')]/ancestor::a")))
    except TimeoutException:
        # Fallback: Click first product in results
        product_link = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@data-component-type='s-search-result']//h2/a)[1]")))
    product_link.click()
    print('Clicked on HP Mouse product.')

    # Step 7: Add to Cart
    add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.ID, 'add-to-cart-button')))
    add_to_cart_btn.click()
    print('Clicked Add to Cart.')

    # Assertion: Check if added to cart
    try:
        cart_confirmation = wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Added to Cart')]")))
        assert 'Added to Cart' in cart_confirmation.text, 'Add to cart confirmation not found.'
        print('Product successfully added to cart.')
    except TimeoutException:
        raise Exception('Add to cart confirmation not found.')

except (TimeoutException, NoSuchElementException, AssertionError, Exception) as e:
    print(f'Error occurred: {e}')
finally:
    # Clean up
    time.sleep(3)
    driver.quit()
    print('WebDriver closed.')

# --- End of Script ---
