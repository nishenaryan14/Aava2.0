from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def add_hp_mouse_to_cart(browser='chrome', base_url='https://www.amazon.com'):
    """
    Automates the process of searching for an HP mouse on Amazon and adding it to the cart.
    Args:
        browser (str): Browser type ('chrome' or 'firefox')
        base_url (str): Amazon base URL
    Returns:
        bool: True if the item was added to cart successfully, False otherwise
    """
    # Initialize WebDriver
    if browser == 'chrome':
        driver = webdriver.Chrome()
    elif browser == 'firefox':
        driver = webdriver.Firefox()
    else:
        raise ValueError('Unsupported browser: {}'.format(browser))

    wait = WebDriverWait(driver, 15)
    success = False

    try:
        # Step 1: Go to Amazon homepage
        driver.get(base_url)
        driver.maximize_window()

        # Step 2: Search for 'HP mouse'
        search_box = wait.until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
        search_box.clear()
        search_box.send_keys('HP mouse')
        search_box.send_keys(Keys.RETURN)

        # Step 3: Wait for search results and select the first 'HP mouse' item
        # Use product title containing 'HP' and 'mouse'
        products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.s-main-slot div[data-component-type="s-search-result"]')))
        item_found = False
        for product in products:
            try:
                title_elem = product.find_element(By.CSS_SELECTOR, 'h2 a span')
                title = title_elem.text.lower()
                if 'hp' in title and 'mouse' in title:
                    # Click on the product link
                    product_link = product.find_element(By.CSS_SELECTOR, 'h2 a')
                    driver.execute_script("arguments[0].scrollIntoView();", product_link)
                    product_link.click()
                    item_found = True
                    break
            except Exception:
                continue

        if not item_found:
            print("No HP mouse found in search results.")
            return False

        # Step 4: Switch to the new tab (Amazon opens product links in a new tab)
        driver.switch_to.window(driver.window_handles[-1])

        # Step 5: Wait for 'Add to Cart' button and click it
        add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.ID, 'add-to-cart-button')))
        add_to_cart_btn.click()

        # Step 6: Validate that the item was added to the cart
        # Wait for confirmation - look for cart count or confirmation message
        time.sleep(3)  # Allow time for cart update
        cart_count_elem = driver.find_element(By.ID, 'nav-cart-count')
        cart_count = int(cart_count_elem.text)
        assert cart_count >= 1, "Cart count did not update as expected."

        print("HP mouse successfully added to cart.")
        success = True

    except Exception as e:
        print(f"Error during Amazon HP mouse add-to-cart test: {e}")
    finally:
        driver.quit()

    return success

if __name__ == "__main__":
    # Example usage: run test on Chrome
    result = add_hp_mouse_to_cart(browser='chrome')
    if result:
        print("Test passed: HP mouse was added to cart.")
    else:
        print("Test failed: HP mouse was NOT added to cart.")