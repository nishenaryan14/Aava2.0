from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def add_hp_mouse_to_cart(browser='chrome', base_url='https://www.amazon.com', search_term='hp mouse'):
    """
    Automates the process of searching for an 'HP Mouse' on Amazon and adding it to the cart.
    Args:
        browser (str): Browser type ('chrome' or 'firefox')
        base_url (str): Amazon site URL
        search_term (str): Product search term
    Returns:
        bool: True if item added to cart successfully, False otherwise
    """
    # Initialize WebDriver
    if browser == 'chrome':
        driver = webdriver.Chrome()
    elif browser == 'firefox':
        driver = webdriver.Firefox()
    else:
        raise ValueError('Unsupported browser type. Use "chrome" or "firefox".')
    
    wait = WebDriverWait(driver, 15)
    added_to_cart = False

    try:
        # Step 1: Navigate to Amazon homepage
        driver.get(base_url)
        driver.maximize_window()

        # Step 2: Search for 'HP Mouse'
        search_box = wait.until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        # Step 3: Wait for search results and select the first relevant HP Mouse
        # Note: Locator chosen for reliability; may need adjustment if Amazon changes UI.
        product_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.s-main-slot div[data-component-type="s-search-result"]')))
        hp_mouse_found = False
        for product in product_list:
            title_elem = product.find_element(By.CSS_SELECTOR, 'h2 a span')
            if 'hp' in title_elem.text.lower() and 'mouse' in title_elem.text.lower():
                product_link = product.find_element(By.CSS_SELECTOR, 'h2 a')
                product_link.click()
                hp_mouse_found = True
                break

        if not hp_mouse_found:
            print('HP Mouse not found in search results.')
            return False

        # Step 4: Switch to the product tab if opened in new tab
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])

        # Step 5: Add to cart
        add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.ID, 'add-to-cart-button')))
        add_to_cart_btn.click()

        # Step 6: Verify item added to cart
        # Wait for confirmation; Amazon may show a side sheet or redirect
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Added to Cart')]")))
            added_to_cart = True
        except:
            # Fallback: Check for cart count increment or confirmation message
            cart_count_elem = driver.find_element(By.ID, 'nav-cart-count')
            if int(cart_count_elem.text) > 0:
                added_to_cart = True

        assert added_to_cart, "Failed to add HP Mouse to cart."
        print("HP Mouse successfully added to cart.")

    except Exception as e:
        print(f"Error during test execution: {e}")
    finally:
        time.sleep(2)
        driver.quit()
    return added_to_cart

if __name__ == "__main__":
    # Example usage
    success = add_hp_mouse_to_cart(browser='chrome')
    if success:
        print("Test Passed: HP Mouse added to cart.")
    else:
        print("Test Failed: HP Mouse not added to cart.")
