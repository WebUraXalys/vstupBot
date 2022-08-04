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
client = pymongo.MongoClient(f"mongodb://{username}:{pwd}@130.61.64.244/vst", tls=True,
                             tlsAllowInvalidCertificates=True)
db = client.vst
coll = db.specs


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.reply("Привіт\n"
                        "Тебе вітає vstupBot. Я створений, щоб допомогти абітурієнтам обрати найкращий університет для вступу на бюджет.")
    # await asyncio.sleep(3.5)

    buttons = [
        types.InlineKeyboardButton(text="Текстовий гайд", url="google.com", callback_data="trusted"),
        types.InlineKeyboardButton(text="Відео гайд", url="youtube.com", callback_data="trusted"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await message.answer("Посилання на інструкцію до бота", reply_markup=keyboard)

    # await asyncio.sleep(5)
    buttons = [
        types.InlineKeyboardButton(text="Так", callback_data="yes"),
        types.InlineKeyboardButton(text="Ні", callback_data="no"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await message.answer("Продовжуємо?", reply_markup=keyboard)


@dp.callback_query_handler(text="yes")
async def check_profession(call: types.CallbackQuery):
    await call.answer()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Так", "Ні"]
    keyboard.add(*buttons)
    await call.message.answer("Ти вже визначився з своєю професією?", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Слава Україні!")
async def slava(message: types.Message):
    await message.reply("Героям слава!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands="get")
async def get_data(message: types.Message):
    # Наразі функціональності не має, циклом хочу перевірити, як працює pymongo
    c = 0
    for value in coll.find():
        if c < 10:
            await message.answer(value["code"] + " " + value["name"])
            await asyncio.sleep(0.05)
            c += 1

@dp.message_handler(commands="help")
async def help_user(message: types.Message):
    await message.reply(
        "Вас вітає vstupBot. Я створений, щоб допомогти абітурієнтам обрати найкращий університет для вступу на бюджет.")


@dp.message_handler(commands="report")
async def send_report(message: types.Message):
    await message.reply("Відправлятиметься репорт")


@dp.message_handler(commands="pay")
async def payment(message: types.Message):
    await message.reply("Я проситиму гроші, коли отримаю картку")


@dp.message_handler()
async def config_user(message: types.Message):
    if message.text == "Ні":
        await message.answer('Рекомендуємо тобі пройти <a href="https://naurok.com.ua/test/yaka-ti-feya-vinks-1455683.html">цей тест</a>', parse_mode="HTML", disable_web_page_preview=True)
    elif message.text == "Так":
        await message.answer("Добра-добра")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
