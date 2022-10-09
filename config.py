from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import Database

host = "127.0.0.1"
user = "postgres"
password = "159953!%((%#"
db_name = 'postgres'


BOT_TOKEN = "5009203412:AAHQUZ7tpkF71skOayRVogI8zqLGTW6OUeU"
DB_FILE = 'database.db'

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
db = Database(DB_FILE)


forbidden_chars = ['_', '@', '/', "\\", '-', '+']
