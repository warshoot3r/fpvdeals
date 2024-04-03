from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class UMTWebScraper:
    def __init__(self, browser='chrome', headless=True, url=None):
        self.browser = browser
        self.headless = headless
        self.url = url
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        
        if self.browser.lower() == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1200")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-extensions")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-features=Translate")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--no-first-run")
            options.add_argument("--incognito")
            options.add_argument("--disable-component-extensions-with-background-pages")
            options.add_argument("--disable-ipc-flooding-protection")
            options.add_argument("--disable-hang-monitor")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--enable-automation")
            options.add_argument("--disable-background-networking")
        elif self.browser.lower() == 'firefox':
            options = webdriver.FirefoxOptions()
        elif self.browser.lower() == 'chromeui':
            options = webdriver.ChromeOptions()
        else:
            raise ValueError("Unsupported browser. Please choose 'chrome' or 'firefox'.")

        if self.headless:
            options.add_argument('--headless=new')

        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--disable-gpu')

        if self.browser.lower() == 'chrome':
            return webdriver.Chrome(options=options)
        elif self.browser.lower() == 'firefox':
            return webdriver.Firefox(options=options)
        elif self.browser.lower() == 'chromeui':
            return webdriver.Chrome(options=options)

    def extract_data(self) -> pd.DataFrame:
        self.driver.get(self.url)
        
        # Wait for the initial set of products to load.
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.snize-product'))
        )

        start_time = time.time()  # Start timing for the timeout check.
        timeout = 20  # Set the timeout to 2 minutes.
        last_height = 0
        while True:
            # Scroll to the bottom of the page
            self.driver.execute_script("window.scrollTo(0, window.pageYOffset + 1000);")
            
            # Wait for the page to load. Adjust the wait time as necessary.
            time.sleep(3)

            # Attempt to wait for the loading indicator to disappear if applicable
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.loading-spinner"))
                )
            except TimeoutException:
                # If the spinner doesn't disappear within the timeout, break the loop
                print("Timed out waiting for the content to load.")
                break

            # Re-evaluate the new height of the page after potentially loading more content
            new_height = self.driver.execute_script("return window.pageYOffset")
            print(f"Exploring web page: New height is {new_height}")

            # Check if the new height is the same as the last height (meaning we're at the bottom)
            if new_height == last_height:
                break
            else:
                last_height = new_height  # Update last_height to the new height for the next iteration
            
            # Check if the script has been running for longer than the timeout duration
            if time.time() - start_time > timeout:
                print("Reached the timeout limit.")
                break

            # Optionally, wait for a specific element that signifies new content has loaded
            # This can help ensure that your script doesn't proceed too quickly before content is ready
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.snize-product'))
                    
                )
                    # After detecting new products, iterate through them to print a summary
                products = self.driver.find_elements(By.CSS_SELECTOR, '.snize-product')
                print("New products detected. Extracting data...")

                # Initialize a temporary list to hold product details for printing
                temp_data_for_printing = []

                for product in products:
                    title = product.find_element(By.CSS_SELECTOR, '.snize-title').get_attribute('textContent').strip() or 'N/A'
                    sku = product.find_element(By.CSS_SELECTOR, '.snize-sku').get_attribute('textContent').replace('SKU: ', '').strip() if product.find_element(By.CSS_SELECTOR, '.snize-sku').get_attribute('textContent') else 'N/A'
                    # Add more details as needed

                    # Append a brief summary of the product to the temporary list
                    temp_data_for_printing.append({'title': title, 'sku': sku})

                # Print out the brief list of new products
                for index, product_summary in enumerate(temp_data_for_printing, start=1):
                    print(f"Product {index}: Title - {product_summary['title']}, SKU - {product_summary['sku']}")
            except TimeoutException:
                                print("Timed out waiting for new products to load.")
                                
            products = self.driver.find_elements(By.CSS_SELECTOR, '.snize-product')

            data = []
            for product in products:
                try:
                    title = product.find_element(By.CSS_SELECTOR, '.snize-title').get_attribute('textContent').strip() or 'N/A'
                except NoSuchElementException:
                    title = 'N/A'
                
                try:
                    sku_text = product.find_element(By.CSS_SELECTOR, '.snize-sku').get_attribute('textContent').strip()
                    sku = sku_text.replace('SKU: ', '') if sku_text else 'N/A'
                except NoSuchElementException:
                    sku = 'N/A'
                
                try:
                    description = product.find_element(By.CSS_SELECTOR, '.snize-description').get_attribute('textContent').strip() or 'N/A'
                except NoSuchElementException:
                    description = 'N/A'
                
                try:
                    price = product.find_element(By.CSS_SELECTOR, '.snize-price').get_attribute('textContent').strip() or 'N/A'
                except NoSuchElementException:
                    price = 'N/A'
                
                try:
                    stock_status = product.find_element(By.CSS_SELECTOR, '.snize-in-stock').get_attribute('textContent').strip() or 'N/A'
                except NoSuchElementException:
                    stock_status = 'N/A'
                
                # Assuming the product link is within the '.snize-product' element, you might need to adjust the selector based on your HTML structure.
                # This attempts to find an <a> tag directly within the product item. Adjust if your structure is different.
                try:
                    href = product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').strip() or 'N/A'
                except NoSuchElementException:
                    href = 'N/A'
                
                details = {
                    'title': title,
                    'sku': sku,
                    'description': description,
                    'price': price,
                    'stock_status': stock_status,
                    'href': href
                }
                
                data.append(details)

        self.quit_driver()  # Close the driver after scraping is complete.
        return pd.DataFrame(data)
    def quit_driver(self):
        self.driver.quit()

# # Example usage
# if __name__ == "__main__":
#     url = 'https://www.unmannedtechshop.co.uk/product-category/parts-sensors/bargain-bin/'
#     scraper = WebScraper(browser='chrome', headless=True, url=url)
#     data_frame = scraper.extract_data()
#     print(data_frame.head())  # Display the first few rows of the scraped data
