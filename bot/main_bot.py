import asyncio

from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv

import markup as nav
from search_machine import search
from user_settings import change_spec, massive_change_spec, change_region, list_the_regions, average_bal
from config import dp, db
from states import ExamsBals, SearchUniver

load_dotenv()


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
    categories_menu = await nav.add_buttons()
    await call.message.edit_text(text="В розробці. Очікуйте в наступних оновленнях", reply_markup=categories_menu)


@dp.callback_query_handler(text_contains="category")
async def category(call: types.CallbackQuery):
    await call.answer()
    data = call.data.split()
    category_id = data[1]
    try:
        page = data[2]
    except:
        page = "1"
    spec_lists = await nav.add_specs(category_id, page)
    await call.message.edit_text(text="Список спеціальностей", reply_markup=spec_lists)


@dp.callback_query_handler(text_contains="spec")
async def add_or_remove_spec(call: types.CallbackQuery):
    await call.answer()
    data = call.data.split()
    spec_code = data[1]
    user_id = call.from_user.id
    await change_spec(call, spec_code)


@dp.callback_query_handler(text="код")
async def specialization(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Пропиши команду /setcode, а тоді через пробіл перечисли номери спеціальностей.\n Приклад: /setcode 011 121 125 123", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands="setcode")
async def set_code(message: types.Message):
    # This code adds list of specialization what user have sent
    list_of_spec = message.text.split()
    await massive_change_spec(message, list_of_spec)


@dp.message_handler(lambda message: message.text == "Продовжити далі" or message.text == "Завершити обирати")
async def choose_region(message: types.Message):
    await message.answer("З спеціальностями покінчено, час перейти до наступного етапу", reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(1.5)
    db.users_specs.update_one({"user_id": message.from_user.id}, {"$unset": {"region": ""}})
    await message.answer("Вам потрібно вибрати одну або кілька областей, де ви хотіли б навчатись. Щоб скасувати вибір області потрібно повторно натиснути на її кнопку", reply_markup=nav.regions)


@dp.callback_query_handler(text_contains="region")
async def add_or_remove_region(call: types.CallbackQuery):
    await call.answer()
    region_name = call.data.split()[1]
    await change_region(call, region_name)



@dp.callback_query_handler(text_contains="The end", state=None)
async def get_exams_result(call: types.CallbackQuery):
    await call.answer()
    if "repeat" not in call.data.split():
        await list_the_regions(call)
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
        if int(history1) != 0 and int(history1) <= 200:
            db.users_specs.update_one({"user_id": message.from_user.id}, {"$set": {"History": int(history1)}})

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
    await call.message.answer("Налаштування завершено. Можливості бота представлено в команді /menu")


@dp.callback_query_handler(text="average")
async def average(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    user_data = db.users_specs.find_one({"user_id": user_id})
    await average_bal(call, user_data)


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
    await search(message, array1)
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
