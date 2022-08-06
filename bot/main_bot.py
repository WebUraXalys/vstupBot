import os
import asyncio
import pymongo
import markup as nav
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)
bots_username = "@test_payment_25435_bot"

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
            parse_mode="HTML", disable_web_page_preview=True, reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(3)
        await message.answer("Тепер ти знаєш, ким хочеш бути?", reply_markup=nav.check_profession_step_2, disable_notification=True)

    elif message.text == "Так":
        await message.answer(
            "Тепер потрібно написати код або коди спеціальностей чи вибрати із списку", reply_markup=nav.specialization)
    else:
        await message.answer("Порадься з батьками, чи що", reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(text="спеціальність")
async def auto_specialization(call: types.CallbackQuery):
    await call.answer()
    # await call.message.answer("Вибери спеціальність", reply_markup=nav.choose_category)
    await call.message.answer(call.message.message_id)


@dp.callback_query_handler(text="код")
async def specialization(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Пропиши команду /setcode, а тоді через пробіл перечисли номери спеціальностей.\n Приклад: /setcode 011 121 125 123", reply_markup=types.ReplyKeyboardRemove())


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
            c.append(f)
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
        db.users_specs.insert_one({'user_id': user_id,
                                   'spec_codes': spec_codes,
                                   'UA': "",
                                   'Math': "",
                                   "History": ""})
        await message.answer("Запис внесено до бази даних")
        await message.answer(f"Вибрано спеціальності: {spec_codes}", reply_markup=nav.cont)
    elif len(result) == 1:
        db.users_specs.update_one({'user_id': user_id}, {'$set': {'spec_codes': spec_codes}})
        await message.answer("Запис в базі даних оновлено")
        await message.answer(f"Вибрано спеціальності: {spec_codes}", reply_markup=nav.cont)


@dp.message_handler(lambda message: message.text == "Продовжити далі")
async def choose_region(message: types.Message):
    await message.answer("З спеціальностями покінчено, час перейти до наступного етапу", reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(1.5)
    db.users_specs.update_one({"user_id": message.from_user.id}, {"$unset": {"region": ""}})
    await message.answer("Вам потрібно вибрати одну або кілька областей, де ви хотіли б навчатись. Щоб скасувати вибір області потрібно повторно натиснути на її кнопку", reply_markup=nav.regions)


@dp.callback_query_handler(text_contains="region")
async def add_or_remove_region(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    data_split = call.data.split()
    region_name = data_split[1]
    if region_name == "АР":
        region_name = "АР Крим"

    res = db.users_specs.find_one({'user_id': user_id})
    try:
        if region_name not in res["region"]:
            print(region_name)
            db.users_specs.update_one({'user_id': user_id}, {"$push": {"region": region_name}})
            if region_name == "Київ" or region_name == "АР Крим":
                await call.message.answer(f"Додано регіон: {region_name}")
            else:
                await call.message.answer(f"Додано регіон: {region_name} область")

        else:
            db.users_specs.update_one({'user_id': user_id}, {"$pull": {"region": region_name}})
            if region_name == "Київ" or region_name == "АР Крим":
                await call.message.answer(f"Видалено регіон: {region_name}")
            else:
                await call.message.answer(f"Видалено регіон: {region_name} область")
    except KeyError:
        db.users_specs.update_one({'user_id': user_id}, {"$push": {"region": region_name}})
        if region_name == "Київ" or region_name == "АР Крим":
            await call.message.answer(f"Додано регіон: {region_name}")
        else:
            await call.message.answer(f"Додано регіон: {region_name} область")


@dp.callback_query_handler(text_contains="The end")
async def get_exams_result(call: types.CallbackQuery):
    await call.answer()
    if "repeat" not in call.data.split():
        mess = "Готово. Ви вибрали наступні регіони:\n"
        regions = db.users_specs.find_one({"user_id": call.from_user.id}, {"_id": 0, "region": 1})
        region_sort = []
        for region in regions["region"]:
            region_sort.append(region)
        region_sort.sort()
        for region in region_sort:
            if region == "АР Крим" or region == "Київ":
                mess += f"✅{region}\n"
            else:
                mess += f"✅{region} область\n"
        await call.message.answer(mess)
    await call.message.answer("Тепер потрібно ввести бали з екзаменів. Наразі доступно лише три предмета, які були на НМТ: українська мова, математика та історія."
                              "Почергово нажміть кожну з кнопок та відповіддю введіть свій бал. Опісля поверніться до цього "
                              "повідомлення та натисність кнопку \"Зберегти\" \n\n",
                              reply_markup=nav.examsMenu)


@dp.callback_query_handler(text_contains="exam")
async def get_exams_result(call: types.CallbackQuery):
    await call.answer()
    exam_mark = call.data.split()
    index = exam_mark[1]
    if index == "ua":
        await call.message.answer("Введіть бал з української мови")
    elif index == "math":
        await call.message.answer("Введіть бал з математики")
    elif index == "history":
        await call.message.answer("Введіть бал з історії")


@dp.message_handler(lambda message: int(message.text) in range(-1000, 1000))
async def push_exam(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Потрібно відправити як відповідь на повідомлення")

    elif message.reply_to_message:
        correct = True
        if int(message.text) != 0 and int(message.text) <= 200:
            separated_text = message.reply_to_message.text.split()
            user_id = message.from_user.id
            if "української" in separated_text:
                await message.answer(f"Бал з української мови: {message.text}")
                db.users_specs.update_one({"user_id": user_id}, {"$set": {"UA": int(message.text)}})
            if "математики" in separated_text:
                await message.answer(f"Бал з математики: {message.text}")
                db.users_specs.update_one({"user_id": user_id}, {"$set": {"Math": int(message.text)}})
            if "історії" in separated_text:
                await message.answer(f"Бал з історії: {message.text}")
                db.users_specs.update_one({"user_id": user_id}, {"$set": {"History": int(message.text)}})

        else:
            correct = False
            if int(message.text) <= 0:
                await message.answer("Бал не може дорівнювати нулю або бути меншим за нього")
            else:
                await message.answer("У вас прекрасні досягнення. Мабуть, вам не потрібна наша допомога, якщо у вас оцінка в більш ніж 200 балів")

    if correct:
        pass
    else:
        await message.answer("Помилка в балах. Виправте свої бали")


@dp.callback_query_handler(text="save")
async def save(call: types.CallbackQuery):
    await call.answer()
    user_coll = db.users_specs.find_one({"user_id": call.from_user.id})

    ua = user_coll["UA"]
    hst = user_coll["History"]
    math = user_coll["Math"]

    await call.message.answer(
        "Введені оцінки \n\n"
        f"Українська мова: {ua},\nІсторія: {hst},\nМатематика: {math}\n\n"
        "Якщо ви помилилися, нажміть кнопку", reply_markup=nav.save)
    await asyncio.sleep(5)
    await call.message.answer("Налаштування завершено")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
