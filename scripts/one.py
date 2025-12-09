import os, sys, time, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Config & Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
USER = os.getenv("AMAZON_USERNAME")
PASS = os.getenv("AMAZON_PASSWORD")
ASIN = os.getenv("AMAZON_ASIN", "B088N8G9RL")
PIN  = os.getenv("AMAZON_PINCODE", "560001")
QTY  = int(os.getenv("AMAZON_QUANTITY", 1))

def require_env():
    missing = [k for k in ("AMAZON_USERNAME", "AMAZON_PASSWORD") if not os.getenv(k)]
    if missing: logging.error(f"Missing env: {', '.join(missing)}"); sys.exit(1)

def wait(driver, by, value, timeout=12):
    try: return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException: logging.error(f"Timeout: {value}"); return None

def click(driver, by, value):
    el = wait(driver, by, value)
    if el: el.click(); return True
    logging.error(f"Not found: {value}"); return False

def login(driver, user, pwd):
    driver.get("https://www.amazon.in/")
    click(driver, By.ID, "nav-link-accountList")
    email = wait(driver, By.ID, "ap_email");  email.send_keys(user)
    click(driver, By.ID, "continue")
    pw = wait(driver, By.ID, "ap_password"); pw.send_keys(pwd)
    click(driver, By.ID, "signInSubmit"); time.sleep(2)
    if any(x in driver.current_url for x in ("authentication", "ap/cvf")):
        raise Exception("Login failed or CAPTCHA.")
    logging.info("Login OK")

def set_pincode(driver, pincode):
    try:
        btns = driver.find_elements(By.ID, "contextualIngressPtLabel_deliveryShortLine")
        if btns:
            btns[0].click()
            pin = wait(driver, By.ID, "GLUXZipUpdateInput"); pin.send_keys(pincode)
            click(driver, By.ID, "GLUXZipUpdate"); time.sleep(1)
            logging.info(f"Pincode set: {pincode}")
    except Exception as e:
        logging.warning(f"Pincode skipped: {e}")

def add_to_cart(driver, qty=1):
    try:
        qty_dd = driver.find_elements(By.ID, "quantity")
        if qty_dd: qty_dd[0].send_keys(str(qty))
    except Exception: pass
    if not click(driver, By.ID, "add-to-cart-button"): raise Exception("Add to cart failed")
    time.sleep(1); click(driver, By.ID, "attach-sidesheet-view-cart-button")

def checkout(driver):
    if not click(driver, By.ID, "hlb-ptc-btn-native"):
        if not click(driver, By.NAME, "proceedToRetailCheckout"):
            raise Exception("Checkout button not found")
    logging.info("Checkout page"); time.sleep(1)

def finalize(driver):
    try:
        addr = driver.find_elements(By.NAME, "shipToThisAddress")
        if addr: addr[0].click(); time.sleep(1)
        logging.info("Reached review order (stop before payment)")
    except Exception as e:
        logging.warning(f"Finalize note: {e}")

def run(user, pwd, asin, pincode, qty):
    driver = None
    try:
        opts = webdriver.ChromeOptions()
        opts.add_argument("--start-maximized")
        # opts.add_argument("--headless=new")  # enable for CI/headless
        driver = webdriver.Chrome(options=opts)
        driver.implicitly_wait(8)

        login(driver, user, pwd)
        driver.get(f"https://www.amazon.in/dp/{asin}")
        set_pincode(driver, pincode)
        add_to_cart(driver, qty)
        checkout(driver)
        finalize(driver)
        logging.info("Flow complete. Review order manually.")
    except Exception as e:
        logging.error(f"Automation failed: {e}")
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    """
    Env:
      AMAZON_USERNAME, AMAZON_PASSWORD (required)
      AMAZON_ASIN (default B088N8G9RL)
      AMAZON_PINCODE (default 560001)
      AMAZON_QUANTITY (default 1)
    """
    require_env()
