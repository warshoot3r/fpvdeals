
#time script
import datetime
import sys


mport datetime
import sys
import time  # Importing time for sleep

# Assuming the scheduled times are the same
scheduled_time_start_hour = 16.5
scheduled_time_end_hour = 17.5

# Current time in hours and minutes as a float
current_time_float = datetime.datetime.now().hour + datetime.datetime.now().minute / 60.0

# Check if current time is within the scheduled window
if scheduled_time_start_hour <= current_time_float < scheduled_time_end_hour:
    print(f"It's time {datetime.datetime.now().strftime('%H:%M')}")
else:
    print(f"Not time. Cancelling {datetime.datetime.now().strftime('%H:%M')}")
    sys.exit()



from modules.umt import UMTWebScraper
from modules.db import UMTDatabase, umtbargainsproductobject
from modules.telegram_bot import TelegramBot
import credentials
telegram = TelegramBot(api_token=credentials.api)

UMTBargainsDBTable = UMTDatabase(TableName="Bargains")



# Assuming UMTBargainsDBTable.return_data_with_time is a method that returns either a pandas DataFrame or None
UMTDATA = UMTBargainsDBTable.return_data_with_time(time_interval='30 Days')

print(UMTDATA)

telegram.send_dataframe_as_file(dataframe=UMTDATA,  file_name="umt", file_format="csv", chat_id=credentials.chat_id)



# Optionally, print UMTDATA for debugging purposes
