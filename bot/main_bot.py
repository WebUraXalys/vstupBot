import os
import asyncio
import pymongo
import markup as nav
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
    await message.reply("Привіт\n"
                        "Тебе вітає vstupBot. Я створений, щоб допомогти абітурієнтам обрати найкращий університет для вступу на бюджет.")
    await asyncio.sleep(3.5)
    await message.answer("Посилання на інструкцію до бота", reply_markup=nav.guideMenu)

    await asyncio.sleep(5)
    await message.answer("Продовжуємо?", reply_markup=nav.continueMenu)


@dp.callback_query_handler(text="yes")
async def check_profession(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Ти вже визначився з своєю професією?", reply_markup=nav.check_profession)


@dp.message_handler(lambda message: message.text == "Так" or message.text == "Ні" or message.text == "Ще ні")
async def check_profession_step_2(message: types.Message):
    if message.text == "Ні":
        await message.answer(
            'Рекомендуємо тобі пройти <a href="https://quizterra.com/ru/kto-ty-iz-vinks">цей тест</a>',
            parse_mode="HTML", disable_web_page_preview=True)
        await asyncio.sleep(3)
        await message.answer("Тепер ти знаєш, ким хочеш бути?", reply_markup=nav.check_profession_step_2, disable_notification=True)

    elif message.text == "Так":
        await message.answer(
            "Тепер потрібно написати код або коди спеціальностей чи вибрати із списку", reply_markup=nav.specialization)
    else:
        await message.answer("Порадься з батьками, чи що")


@dp.callback_query_handler(text="спеціальність")
async def specialnist(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Заїбусь з цим точно")
    await call.message.answer(call.message.message_id)


@dp.callback_query_handler(text="код")
async def specialnist(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Пропиши команду /set_code, а тоді через пробіл перечисли номери спеціальностей.\n Приклад: /set_code 011 121 125 123")
    await call.message.answer(call.message.message_id)


@dp.message_handler(commands="setcode")
async def set_code(message: types.Message):
    # This code adds list of specialization what user have sent
    spec_codes = []
    list_of_spec = message.text.split()
    user_id = message.from_user.id

    for value in list_of_spec[1::]:
        # Code checks does specialization exist and add it to list of chosen ones
        finder = coll.find({'name': {"$regex": value}}, {'_id': 0, "name": 1})
        c = []
        for f in finder:
            c.append(coll)
        if len(c) == 1:
            spec_codes.append(value)
        elif len(c) < 1:
            await message.reply(f"Такої спеціальності нема: {value}")

    # Work with database. Firstly we check does user exist in our db.
    # Then we create or update document in collection. It depends on result from previous step
    res = db.users_specs.find({'user_id': user_id})
    result = []
    for r in res:
        result.append(r)
    if len(result) < 1:
        await message.answer("Нема запису")
        db.users_specs.insert_one({'user_id': user_id,
                                   'spec_codes': spec_codes})
        await message.answer("Запис внесено до бази даних")
        await message.answer(f"Вибрано спеціальності: {spec_codes}")
    elif len(result) == 1:
        db.users_specs.update_one({'user_id': user_id}, {'$set': {'spec_codes': spec_codes}})
        await message.answer("Запис в базі даних оновлено")
        await message.answer(f"Вибрано спеціальності: {spec_codes}")



@dp.message_handler(commands="get_id")
async def get_id(message: types.Message):
    await message.answer(message.reply_to_message.message_id)


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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
