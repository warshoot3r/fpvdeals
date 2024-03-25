from modules.umt import UMTWebScraper
from modules.db import UMTDatabase, umtbargainsproductobject
from modules.telegram_bot import TelegramBot
import credentials
telegram = TelegramBot(api_token=credentials.api)


UMTBargainsDBTable = UMTDatabase(TableName="Bargains")

print(UMTBargainsDBTable.return_data())