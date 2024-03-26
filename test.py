from modules.umt import UMTWebScraper
from modules.db import UMTDatabase, umtbargainsproductobject
from modules.telegram_bot import TelegramBot






UMTBargainsurl = 'https://www.unmannedtechshop.co.uk/product-category/parts-sensors/bargain-bin/'
UMTBargains = UMTWebScraper(browser='chrome', headless=True, url=UMTBargainsurl)
UMTBargainsDBTable = UMTDatabase(TableName="Bargains")
