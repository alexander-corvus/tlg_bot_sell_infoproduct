from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv
from logs.logs_settings import logger
import os

if not find_dotenv():
    logger.error(f'.env is missing: {__file__}, 9')
    exit('Environment variables not loaded because .env file is missing')
else:
    load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID_1 = int(os.getenv('ADMIN_ID_1'))
ADMIN_ID_2 = int(os.getenv('ADMIN_ID_2'))
YOOKASSA_TOKEN = os.getenv('YOOKASSA_TEST')

storage = MemoryStorage()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot, storage=storage)
