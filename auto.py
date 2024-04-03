
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
      description= getattr(new_product, "description"),
      href=getattr(new_product, "href")
    ))



#import data and update table
for listing in bargains_objects:
    UMTBargainsDBTable.import_data(data_to_import=listing, unique_key="sku")

# Assuming UMTBargainsDBTable.return_data_with_time is a method that returns either a pandas DataFrame or None
UMTDATA = UMTBargainsDBTable.return_data_with_time(time_interval='20 minutes')

# Check if UMTDATA is not None before checking if it's empty
if UMTDATA is not None:
    if not UMTDATA.empty:
        try:
            # Your data processing and sending logic here
            sorted_filtered_data = UMTDATA.sort_values(by=["Price", "Condition", "Reason"], ascending=[True, False, False])
            sorted_filtered_data = sorted_filtered_data.drop(columns=["Description", "id", "SKU", "LastUpdated", "StockStatus", "TotalPriceReduction"])
            telegram.send_message(chat_id=credentials.chat_id, message="Updated UMT bargains has new information")
            # telegram.send_dataframe(chat_id=credentials.chat_id, dataframe=sorted_filtered_data)
            telegram.send_href_formatted_dataframe(chat_id=credentials.chat_id, show_columns=["Title", "Price","Reason","Condition"],dataframe=sorted_filtered_data)

        except Exception as e:
            print(f"An error occurred while processing or sending data: {e}", flush=True)
    else:
        print("No data in table so not sending any data", flush=True)
else:
    print("UMTDATA is None, indicating no data was returned.", flush=True)





# Optionally, print UMTDATA for debugging purposes
print(UMTDATA)
