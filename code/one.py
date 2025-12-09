from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def amazon_login_search_add_to_cart():
    # Setup WebDriver (assuming Chrome)
    service = Service('/path/to/chromedriver')  # Update this path
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    try:
        # Navigate to Amazon
        driver.get('https://www.amazon.com')
        
        # Login
        sign_in_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "nav-link-accountList"))
        )
        sign_in_link.click()
        
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_input.send_keys('demo_user')
        
        continue_btn = driver.find_element(By.ID, "continue")
        continue_btn.click()
        
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys('demo_pass')
        
        signin_btn = driver.find_element(By.ID, "signInSubmit")
        signin_btn.click()
        
        # Verify login success
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "nav-link-accountList-nav-line-1"))
            )
            print("Login successful!")
        except TimeoutException:
            print("Login failed or took too long.")
            return
        
        # Search for HP mouse
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        search_box.clear()
        search_box.send_keys("HP mouse")
        
        search_btn = driver.find_element(By.ID, "nav-search-submit-button")
        search_btn.click()
        
        # Click on the first product
        first_product = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-index='1']//h2/a"))
        )
        first_product.click()
        
        # Add to cart
        add_to_cart_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
        )
        add_to_cart_btn.click()
        
        # Verify item added to cart
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "nav-cart-count"))
            )
            cart_count = driver.find_element(By.ID, "nav-cart-count").text
            if int(cart_count) > 0:
                print("Item successfully added to cart!")
            else:
                print("Failed to add item to cart.")
        except (TimeoutException, NoSuchElementException):
            print("Could not verify if item was added to cart.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    amazon_login_search_add_to_cart()
