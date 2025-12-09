# selenium_amazon_search.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time
import sys

# Setup Chrome WebDriver (make sure chromedriver is installed and in PATH)
def setup_driver():
    try:
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except WebDriverException as e:
        print(f"WebDriver setup failed: {e}")
        sys.exit(1)

def search_amazon_for_laptop(driver):
    try:
        driver.get('https://www.amazon.com')
        time.sleep(2)  # Wait for page to load
        search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
        search_box.send_keys('laptop')
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for results to load
        # Assertion: Check that search results contain 'laptop'
        results = driver.find_elements(By.CSS_SELECTOR, 'span.a-size-medium.a-color-base.a-text-normal')
        assert any('laptop' in result.text.lower() for result in results), "No search results for 'laptop' found."
        print("Search for 'laptop' successful. Results found.")
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
    except AssertionError as e:
        print(f"Assertion failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    driver = setup_driver()
    search_amazon_for_laptop(driver)
