from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import time
import subprocess

# Function to get the path to ChromeDriver
def get_chromedriver_path():
    result = subprocess.run(["which", "chromedriver"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stderr:
        raise FileNotFoundError("ChromeDriver not found. Please install ChromeDriver and ensure it's in your PATH.")
    return result.stdout.decode("utf-8").strip()

# Initialize the Chrome WebDriver with options
chrome_driver_path = get_chromedriver_path()
service = Service(executable_path=chrome_driver_path)
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')  # Runs Chrome in headless mode. Comment out if you want to see the browser window.

driver = webdriver.Chrome(service=service, options=options)

# URL of the page to scrape
url = 'https://www.unmannedtechshop.co.uk/product-category/parts-sensors/bargain-bin/'

# Open the webpage
driver.get(url)

# Wait for dynamic content to load
time.sleep(5)  # Adjust based on your network speed

# Scroll to the bottom to ensure all products are loaded (if the page has lazy loading)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Allow time for any dynamic content to load after scrolling
time.sleep(5)  # Adjust based on your network speed

# Find all product items
products = driver.find_elements(By.CSS_SELECTOR, '.snize-product')

# Prepare data for CSV
data = []
for product in products:
    try:
        title = product.find_element(By.CSS_SELECTOR, '.snize-title').text
    except Exception:
        title = "N/A"
    try:
        sku = product.find_element(By.CSS_SELECTOR, '.snize-sku').text.replace('SKU: ', '')
    except Exception:
        sku = "N/A"
    try:
        description = product.find_element(By.CSS_SELECTOR, '.snize-description').text
    except Exception:
        description = "N/A"
    try:
        price = product.find_element(By.CSS_SELECTOR, '.snize-price').text
    except Exception:
        price = "N/A"
    try:
        stock_status = product.find_element(By.CSS_SELECTOR, '.snize-in-stock').text
    except Exception:
        stock_status = "N/A"

    data.append([title, sku, description, price, stock_status])

# Close the browser
driver.quit()

# Write data to CSV file
csv_file_path = 'products.csv'
with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'SKU', 'Description', 'Price', 'Stock Status'])  # Header
    writer.writerows(data)

print(f"Data scraped successfully. {len(data)} products found.")

