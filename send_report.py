
#time script
import datetime
import sys


scheduled_time_start_hour = 16.5
scheduled_starttime = f"{int(scheduled_time_start_hour)}:{int((scheduled_time_start_hour-int(scheduled_time_start_hour))*60):02d}"
start_time = datetime.datetime.strptime(scheduled_starttime, '%H:%M').strftime('%H:%M')

scheduled_time_end_hour = 17.5
scheduled_endtime = f"{int(scheduled_time_end_hour)}:{int(((scheduled_time_end_hour)-int(scheduled_time_end_hour))*60):02d}"
end_time = datetime.datetime.strptime(scheduled_endtime, '%H:%M').strftime('%H:%M')

print(f"Scheduled time is {scheduled_starttime} to {scheduled_endtime}. Machine time -> {datetime.datetime.now().strftime('%H:%M')}")
while True:
        current_time = datetime.datetime.now()
        # Calculate the time difference between local time and GM
        time_str = current_time.strftime('%H:%M')

        if  start_time <= time_str < end_time:

            print(f"It's time {time_str}", flush=True)
            break

        else:
            print(f"Not time. Cancelling {time_str}", flush=True)
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
