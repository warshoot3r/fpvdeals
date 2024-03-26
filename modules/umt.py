from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time
import pandas as pd

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
        else:
            raise ValueError("Unsupported browser. Please choose 'chrome' or 'firefox'.")

        if self.headless:
            options.add_argument('--headless')

        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--disable-gpu')

        if self.browser.lower() == 'chrome':
            return webdriver.Chrome(options=options)
        elif self.browser.lower() == 'firefox':
            return webdriver.Firefox(options=options)

    def extract_data(self)-> pd.DataFrame:
        self.driver.get(self.url)
        time.sleep(5)  # Wait for the dynamic content to load
        
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for any dynamic content to load after scrolling
        
        products = self.driver.find_elements(By.CSS_SELECTOR, '.snize-product')
        data = []
        for product in products:
            details = {
                'title': product.find_element(By.CSS_SELECTOR, '.snize-title').get_attribute('textContent') or 'N/A',
                'sku': product.find_element(By.CSS_SELECTOR, '.snize-sku').get_attribute('textContent').replace('SKU: ', '') if product.find_element(By.CSS_SELECTOR, '.snize-sku').get_attribute('textContent') else 'N/A',
                'description': product.find_element(By.CSS_SELECTOR, '.snize-description').get_attribute('textContent') or 'N/A',
                'price': product.find_element(By.CSS_SELECTOR, '.snize-price').get_attribute('textContent') or 'N/A',
                'stock_status': product.find_element(By.CSS_SELECTOR, '.snize-in-stock').get_attribute('textContent') or 'N/A'
            }
            data.append(details)

        self.quit_driver()  # Close the driver after scraping
        return pd.DataFrame(data)
    def quit_driver(self):
        self.driver.quit()

# # Example usage
# if __name__ == "__main__":
#     url = 'https://www.unmannedtechshop.co.uk/product-category/parts-sensors/bargain-bin/'
#     scraper = WebScraper(browser='chrome', headless=True, url=url)
#     data_frame = scraper.extract_data()
#     print(data_frame.head())  # Display the first few rows of the scraped data
