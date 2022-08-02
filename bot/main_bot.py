import os
import pymongo
from aiogram import Bot, Dispatcher, executor, types

from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

# Preparing for using MongoDB
client = pymongo.MongoClient('130.61.64.244', tls=True, tlsAllowInvalidCertificates=True)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.reply("Привіт.")


@dp.message_handler(commands="help")
async def help_user(message: types.Message):
    await message.reply("Вас вітає vstupBot. Я створений, щоб допомогти абітурієнтам обрати найкращий університет для вступу на бюджет.")


@dp.message_handler(commands="report")
async def send_report(message: types.Message):
    await message.reply("Відправлятиметься репорт")


@dp.message_handler(commands="pay")
async def payment(message: types.Message):
    await message.reply("Я проситиму гроші, коли отримаю картку")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
