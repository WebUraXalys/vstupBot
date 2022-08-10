import os

import pymongo
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Preparing for using MongoDB
username = os.getenv('user_name')
pwd = os.getenv('pwd')
client = pymongo.MongoClient(f"mongodb://{username}:{pwd}@130.61.64.244/vst", tls=True, tlsAllowInvalidCertificates=True)
db = client.vst
