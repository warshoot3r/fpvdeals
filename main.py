from modules.umt import UMTWebScraper
from modules.db import UMTDatabase

UMTBargainsurl = 'https://www.unmannedtechshop.co.uk/product-category/parts-sensors/bargain-bin/'
UMTBargains = UMTWebScraper(browser='chrome', headless=True, url=UMTBargainsurl)
data_frame = UMTBargains.extract_data()


UMTBargainsDBTable = UMTDatabase(TableName="Bargains")


UMTBargainsDBTable.update_table()