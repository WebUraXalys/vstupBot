import os
import asyncio
import pymongo
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

# Preparing for using MongoDB
username = os.getenv('user_name')
pwd = os.getenv('pwd')
client = pymongo.MongoClient(f"mongodb://{username}:{pwd}@130.61.64.244/vst", tls=True, tlsAllowInvalidCertificates=True)
db = client.vst
coll = db.specs


@dp.message_handler(commands="start")
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Слава Україні!"]
    keyboard.add(*buttons)
    await message.reply("Привіт, абітурієнте.", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Слава Україні!")
async def slava(message: types.Message):
    await message.reply("Героям слава!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands="get")
async def get_data(message: types.Message):
    # Наразі функціональності не має, циклом хочу перевірити, як працює pymongo
    c = 0
    for value in coll.find():
        if c < 5:
            await message.answer(value["code"] + value["name"])
            await asyncio.sleep(1)
            c += 1


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
