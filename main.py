from modules.umt import UMTWebScraper
from modules.db import UMTDatabase, umtbargainsproductobject


UMTBargainsurl = 'https://www.unmannedtechshop.co.uk/product-category/parts-sensors/bargain-bin/'
UMTBargains = UMTWebScraper(browser='chrome', headless=True, url=UMTBargainsurl)
UMTBargainsDBTable = UMTDatabase(TableName="Bargains")

#scrape data
data_frame = UMTBargains.extract_data()

#parse to objects and create object
bargains_objects = list()
for new_product in data_frame.itertuples():

    bargains_objects.append(umtbargainsproductobject(.
      title= getattr(new_product, 'title'), 
      price=getattr(new_product, "price"),
      sku=getattr(new_product, "sku"), 
      stockstatus=getattr(new_product, "stock_status"),
      description= getattr(new_product, "description")
    ))



#import data and update table
for listing in bargains_objects:
    UMTBargainsDBTable.import_data(data_to_import=listing, unique_key="sku")

UMTDATA = UMTBargainsDBTable.return_data()
print(UMTDATA)