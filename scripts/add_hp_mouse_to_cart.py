from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def add_hp_mouse_to_cart(browser='chrome', amazon_url='https://www.amazon.com'):
    """
    Automates the process of searching for an HP mouse and adding it to the cart on Amazon.
    
    Args:
        browser (str): Browser type ('chrome' or 'firefox').
        amazon_url (str): URL of the Amazon homepage.
    Returns:
        bool: True if product added to cart successfully, False otherwise.
    """
    driver = None
    try:
        # Browser setup
        if browser == 'chrome':
            driver = webdriver.Chrome()
        elif browser == 'firefox':
            driver = webdriver.Firefox()
        else:
            raise ValueError('Unsupported browser: {}'.format(browser))
        
        driver.maximize_window()
        driver.get(amazon_url)
        
        # Wait for search bar to be present
        wait = WebDriverWait(driver, 15)
        search_box = wait.until(
            EC.presence_of_element_located((By.ID, 'twotabsearchtextbox'))
        )
        
        # Search for "HP Mouse"
        search_box.clear()
        search_box.send_keys('HP Mouse')
        search_box.send_keys(Keys.RETURN)
        
        # Wait for search results
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
        )
        time.sleep(2)  # Allow extra time for dynamic content
        
        # Find the first HP Mouse product (refined by checking title contains 'HP')
        products = driver.find_elements(By.CSS_SELECTOR, "span.a-size-medium.a-color-base.a-text-normal")
        hp_mouse_link = None
        for product in products:
            if 'hp' in product.text.lower() and 'mouse' in product.text.lower():
                hp_mouse_link = product
                break
        
        if not hp_mouse_link:
            print("No HP Mouse found in search results.")
            return False
        
        # Click product link
        hp_mouse_link.click()
        
        # Switch to new tab if opened
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])
        
        # Wait for Add to Cart button
        add_to_cart_btn = wait.until(
            EC.element_to_be_clickable((By.ID, 'add-to-cart-button'))
        )
        
        # Click Add to Cart
        add_to_cart_btn.click()
        
        # Wait for cart confirmation
        cart_msg = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1, div#sw-atc-details-single-container"))
        )
        
        # Validate addition to cart
        page_source = driver.page_source.lower()
        success = 'added to cart' in page_source or 'added to your cart' in page_source
        assert success, "HP Mouse not added to cart successfully."
        
        print("HP Mouse added to cart successfully!")
        return True
        
    except Exception as e:
        print(f"Error during Amazon add-to-cart test: {e}")
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Example usage
    result = add_hp_mouse_to_cart(browser='chrome')
    print("Test result:", "PASS" if result else "FAIL")
