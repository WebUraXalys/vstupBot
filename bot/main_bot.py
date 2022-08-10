import asyncio
import os

import pymongo
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from states import ExamsBals, SearchUniver
from dotenv import load_dotenv

import markup as nav

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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


@dp.callback_query_handler(text="no")
async def finish_process(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Гаразд. Роботу завершено")


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
    await call.message.answer("В розробці. Очікуйте в наступних оновленнях")


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


@dp.callback_query_handler(text_contains="The end", state=None)
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
    await call.message.answer("Тепер нам потрібно дізнатись ваші результати НМТ, щоб вирахувати середній бал для вибраної спеціальності.")
    await call.message.answer("Введіть бал з української мови")
    await ExamsBals.ua.set()


@dp.message_handler(state=ExamsBals.ua)
async def get_ua(message: types.Message, state=FSMContext):
    ua1 = message.text
    finita_la_comedia = False

    try:
        if int(ua1) <= 100 or int(ua1) > 200:
            correct_ua = False
        else:
            correct_ua = True
    except ValueError:
        await message.answer("Неправильний тип даних. Потрібно вводити тільки число. Повторіть спробу")
        finita_la_comedia = True
    if finita_la_comedia:
        pass
    else:
        await state.update_data(ua=ua1, correct_ua=correct_ua)

        await message.answer("Введіть бал з математики")
        await ExamsBals.next()


@dp.message_handler(state=ExamsBals.math)
async def get_math(message: types.Message, state=FSMContext):
    math1 = message.text
    finita_la_comedia = False
    try:
        if int(math1) <= 100 or int(math1) > 200:
            correct_math = False
        else:
            correct_math = True
    except ValueError:
        await message.answer("Неправильний тип даних. Потрібно вводити тільки число. Повторіть спробу")
        finita_la_comedia = True
    if finita_la_comedia:
        pass
    else:
        await state.update_data(math=math1, correct_math=correct_math)

        await message.answer("Введіть бал з історії")
        await ExamsBals.next()


@dp.message_handler(state=ExamsBals.history)
async def get_history(message: types.Message, state=FSMContext):
    history1 = message.text
    finita_la_comedia = False

    await state.update_data(history=history1)
    try:
        if int(history1) == 0 or int(history1) > 200:
            correct = False
        else:
            correct = True
    except ValueError:
        await message.answer("Неправильний тип даних. Потрібно вводити тільки число. Повторіть спробу")
        finita_la_comedia = True
    if finita_la_comedia:
        pass
    else:
        data = await state.get_data()
        if int(data.get("ua")) != 0 and int(data.get("ua")) <= 200:
            db.users_specs.update_one({"user_id": message.from_user.id}, {"$set": {"UA": int(data.get("ua"))}})

        if int(data.get("math")) != 0 and int(data.get("math")) <= 200:
            db.users_specs.update_one({"user_id": message.from_user.id}, {"$set": {"Math": int(data.get("math"))}})
        if int(data.get("history")) != 0 and int(data.get("history")) <= 200:
            db.users_specs.update_one({"user_id": message.from_user.id}, {"$set": {"History": int(data.get("history"))}})

        if not correct or not data.get("correct_math") or not data.get("correct_ua"):
            await message.answer("Десь ви зробили помилку. Перевірте свої відповіді та виправте їх", reply_markup=nav.fix)
        else:
            user_coll = db.users_specs.find_one({"user_id": message.from_user.id})

            ua = user_coll["UA"]
            hst = user_coll["History"]
            math = user_coll["Math"]

            await message.answer(
                "Готово. Перевірте свої бали. Якщо все правильно, нажміть зберегти \n\n"
                f"Українська мова: {ua},\nІсторія: {hst},\nМатематика: {math}\n\n"
                "Якщо ви помилилися, нажміть кнопку", reply_markup=nav.save)
        await state.finish()


@dp.callback_query_handler(text="save")
async def save(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Налаштування завершено")


@dp.callback_query_handler(text="average")
async def average(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    user_data = db.users_specs.find_one({"user_id": user_id})
    specialization = user_data["spec_codes"]
    regions = []

    for item in user_data["region"]:
        if item == "Київ":
            regions.append("КИЇВ")
        elif item == "АР Крим":
            pass
        else:
            regions.append(item + " область")

    for region in regions:
        for spec_item in specialization:
            find_univ = db.univs.find({"region": region, "specs": {"$elemMatch": {"spec_code": spec_item}}})
            for objection in find_univ:
                for specialization in objection['specs']:
                    if spec_item == specialization['spec_code']:
                        for exam_requirement in specialization['contest_subjects']:
                            if exam_requirement['name'] == 'Українська мова':
                                ua_koef = exam_requirement['koef']
                            if exam_requirement['name'] == 'Математика':
                                math_koef = exam_requirement['koef']
                            if exam_requirement['name'] == 'Історія України':
                                history_koef = exam_requirement['koef']
                        average_enjoyer = int(user_data['UA'])*ua_koef + int(user_data['Math'])*math_koef + int(user_data['History'])*history_koef
                        try:
                            await call.message.answer(f"Назва університету: {objection['name']}\n"
                                                 f"Регіон: {objection['region']}\n"
                                                 f"Спеціальність: {specialization['spec_name']} {specialization['spec_code']}\n"
                                                 f"Код закладу: {objection['code']}\n\n"
                                                 f"<b>Cтатистика закладу</b>\n"
                                                 f"Загальна кількість місць:{specialization['stat']['statm_all_count']}\n"
                                                 f"З них бюджет:{specialization['stat']['statm_budget']}\n"
                                                 f"Подано заяв:{specialization['stat']['statm_admitted']}\n"
                                                 f"Максимальний бал: {specialization['stat']['mark_max']}\n"
                                                 f"Cередній бал: {specialization['stat']['mark_avg']}\n"
                                                 f"Мінімальний бал: {specialization['stat']['mark_min']}\n"
                                                 f"Ваш середній бал:{average_enjoyer}\n", parse_mode="HTML", disable_notification=True)
                            await asyncio.sleep(1)
                        except KeyError:
                            await call.message.answer(f"Назва університету: {objection['name']}\n"
                                                 f"Регіон: {objection['region']}\n"
                                                 f"Спеціальність: {specialization['spec_name']} {specialization['spec_code']}\n"
                                                 f"Код закладу: {objection['code']}\n\n"
                                                 f"Заклад не надав статистику\n"
                                                 f"Ваш середній бал:{average_enjoyer}\n", disable_notification=True)
                            await asyncio.sleep(1)


@dp.message_handler(commands="menu")
async def menu(message: types.Message):
    await message.answer("Меню бота, ще буде доповнюватись", reply_markup=nav.mainMenu)


@dp.callback_query_handler(text="search", state=None)
async def search_uni(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Введіть скорочену назву навчального закладу")
    await SearchUniver.name.set()


@dp.message_handler(state=SearchUniver.name)
async def find_univer(message: types.Message, state=FSMContext):
    array1 = message.text.split()
    univers = db.univs.find({"short_name": {"$in": array1}})
    for univer in univers:
        await message.answer("Інформація щодо університету\n"
                             f"Назва: {univer['name']}\n"
                             f"Регіон:{univer['region']}")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
