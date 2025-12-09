from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def amazon_login_search_add_to_cart():
    # Setup WebDriver
    service = Service('/path/to/chromedriver')  # Update this path
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    try:
        # Navigate to Amazon
        driver.get('https://www.amazon.com/')
        
        # Click on Sign In
        sign_in_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "nav-link-accountList"))
        )
        sign_in_link.click()
        
        # Login
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_field.send_keys('demo_user')
        email_field.send_keys(Keys.RETURN)
        
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_field.send_keys('demo_pass')
        password_field.send_keys(Keys.RETURN)
        
        # Verify login success
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-link-accountList-nav-line-1"))
        )
        print("Login successful!")
        
        # Search for HP mouse
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        search_box.send_keys("HP mouse")
        search_box.send_keys(Keys.RETURN)
        
        # Select the first HP mouse from the search results
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-component-type='s-search-result'] h2 a"))
        )
        first_result.click()
        
        # Add to cart
        add_to_cart_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
        )
        add_to_cart_button.click()
        
        # Verify item added to cart
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-cart-count"))
        )
        cart_count = driver.find_element(By.ID, "nav-cart-count").text
        assert int(cart_count) > 0, "Item was not added to cart"
        print("HP mouse successfully added to cart!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    amazon_login_search_add_to_cart()