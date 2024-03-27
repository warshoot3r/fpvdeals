
from modules.umt import UMTWebScraper
from modules.db import UMTDatabase, umtbargainsproductobject
from modules.telegram_bot import TelegramBot
import credentials
telegram = TelegramBot(api_token=credentials.api)


UMTBargainsurl = 'https://www.unmannedtechshop.co.uk/product-category/parts-sensors/bargain-bin/'
UMTBargains = UMTWebScraper(browser='chrome', headless=True, url=UMTBargainsurl)
UMTBargainsDBTable = UMTDatabase(TableName="Bargains")



#scrape data
#parse to objects and crfeate object
data_frame = UMTBargains.extract_data()
bargains_objects = list()
for new_product in data_frame.itertuples():

    bargains_objects.append(umtbargainsproductobject(
      title= getattr(new_product, 'title'), 
      price=getattr(new_product, "price"),
      sku=getattr(new_product, "sku"), 
      stockstatus=getattr(new_product, "stock_status"),
      description= getattr(new_product, "description")
    ))



#import data and update table
for listing in bargains_objects:
    UMTBargainsDBTable.import_data(data_to_import=listing, unique_key="sku")

UMTDATA = UMTBargainsDBTable.return_data_with_time(time_interval='20 minutes')
if UMTDATA.empty:
  print("No data in table so not sending any data", flush=True)
else:
  telegram.send_message(chat_id=credentials.chat_id, message="Updated UMT bargains has new information \!")
  telegram.send_dataframe(chat_id=credentials.chat_id, exclude_columns=["Description","id","SKU", "LastUpdated","StockStatus", "TotalPriceReduction"], dataframe=UMTDATA.sort_values(by=["Price","Condition"], ascending=[True, False]))
print(UMTDATA)