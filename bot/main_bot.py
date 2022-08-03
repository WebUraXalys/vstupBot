import os
import pymongo
from aiogram import Bot, Dispatcher, executor, types
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

# Preparing for using MongoDB
# Є ще проблема з підключенням до бази. Буду вирішувати
# pymongo.errors.InvalidURI: Username and password must be escaped according to RFC 3986, use urllib.parse.quote_plus
client = pymongo.MongoClient("Адресу так дам, не буду ж пароль зливати", tls=True, tlsAllowInvalidCertificates=True)
db = client.vst
coll = db.specs


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.reply("Привіт.")


@dp.message_handler(commands="get")
async def get_data(message: types.Message):
    # Наразі функціональності не має, циклом хочу перевірити, як працює pymongo
    c = 0
    if c<10:
        for value in coll.find():
            await message.reply(value)
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
