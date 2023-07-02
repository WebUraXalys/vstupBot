import asyncio
from dotenv import load_dotenv
from aiogram import executor, types
from aiogram.dispatcher import FSMContext

import markup as nav
from config import dp, db
from search_machine import search
from logic import average_bal, user_position, list_the_regions
from states import ExamsMarks, SearchUniver, FirstName, SpecCodes, StartProcess
from user_settings import change_spec, massive_change_spec, change_region, ap_univer, set_fn

load_dotenv()


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.reply("Привіт\n"
                        "Тебе вітає vstupBot. Я створений, щоб допомогти абітурієнтам обрати найкращий університет для вступу на бюджет та стежити за місцем в рейтингу")
    await asyncio.sleep(3.5)
    # await message.answer("Посилання на інструкцію до бота", reply_markup=nav.guideMenu)
    #
    # await asyncio.sleep(5)
    await message.answer("Продовжуємо?", reply_markup=nav.continueMenu)


@dp.callback_query_handler(text="yes",  state=None)
async def check_profession(call: types.CallbackQuery):
    await call.answer()
    await StartProcess.agreement.set()
    await call.message.answer("Ти вже визначився з своєю професією?", reply_markup=nav.check_profession)


@dp.callback_query_handler(text="no")
async def finish_process(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Гаразд. Роботу завершено")


@dp.message_handler(state=StartProcess.agreement)
async def check_profession_step_2(message: types.Message, state=FSMContext):
    if message.text == "Ні":
        await message.answer(
            'Якщо ти ще не впевнений, рекомендуємо тобі пройти <a href="https://cdn.kname.edu.ua/index.php/abituriientu/test-z-proforiientatsii">цей тест</a>. Коли завершиш, повернись сюди й ми продовжимо роботу ',
            parse_mode="HTML", disable_web_page_preview=True)
        await asyncio.sleep(3)
        await message.answer("Тепер ти знаєш, ким хочеш бути?", reply_markup=nav.check_profession_step_2, disable_notification=True)

    elif message.text == "Так":
        await message.answer(
            "Тепер потрібно написати код або коди спеціальностей чи вибрати із списку", reply_markup=nav.specialization)
        await state.finish()
    elif message.text == "Ще ні":
        categories_menu = await nav.add_buttons()
        await message.answer("Порадься з батьками, вчителем чи з кимось, чия думка для тебе є авторитетною. Однак ти можеш переглянути список категорій й вибрати ту, яка тобі найбільше сподобається", reply_markup=categories_menu)
    elif message.text == "Завершити":
        await state.finish()
        await message.answer("Роботу завершено")
    else: await message.answer("Я розумію тільки окремі фрази. Будь ласка, використовуйте кнопки з готовими словами")


@dp.callback_query_handler(text="спеціальність")
async def auto_specialization(call: types.CallbackQuery):
    await call.answer()
    categories_menu = await nav.add_buttons()
    await call.message.edit_text(text="Для початку оберіть категорію. Там ви знайдете список спеціальностей. Якщо ви вибрали не ту спеціальність, натисніть на кнопку ще раз, щоб її видалити", reply_markup=categories_menu)


@dp.callback_query_handler(text_contains="category")
async def category(call: types.CallbackQuery):
    await call.answer()
    data = call.data.split()
    category_id = data[1]
    try:
        page = data[2]
    except IndexError:
        page = "1"
    spec_lists = await nav.add_specs(category_id, page)
    await call.message.edit_text(text="Оберіть спеціальність з списку. Щоб скасувати вибір, нажміть на кнопку спеціальності ще раз", reply_markup=spec_lists)


@dp.callback_query_handler(text_contains="spec")
async def add_or_remove_spec(call: types.CallbackQuery):
    await call.answer()
    data = call.data.split()
    spec_code = data[1]
    await change_spec(call, spec_code)


@dp.callback_query_handler(text="код", state=None)
async def specialization(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Через кому перечисли коди спеціальностей. Обов'язково залиште пробіл після розділового знаку\n\n"
                              "Приклад: 011, 121, 125, 123", reply_markup=types.ReplyKeyboardRemove())
    await SpecCodes.codes.set()


@dp.message_handler(state=SpecCodes.codes)
async def set_code(message: types.Message, state=FSMContext):
    list_of_spec = message.text.split(", ")
    await massive_change_spec(message, list_of_spec)
    await state.finish()


@dp.message_handler(lambda message: message.text == "Продовжити далі" or message.text == "Завершити обирати")
async def choose_region(message: types.Message):
    await message.answer("З спеціальностями покінчено, час перейти до наступного етапу", reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(1.5)
    db.users_specs.update_one({"user_id": message.from_user.id}, {"$unset": {"region": ""}})
    buttons = await nav.regions_buttons(callback="The end")
    await message.answer("Вам потрібно вибрати одну або кілька областей, де ви хотіли б навчатись. Щоб скасувати вибір області потрібно повторно натиснути на її кнопку", reply_markup=buttons)


@dp.callback_query_handler(text_contains="change")
async def call_choose_region(call: types.CallbackQuery):
    await call.answer()
    db.users_specs.update_one({"user_id": call.from_user.id}, {"$unset": {"region": ""}})
    text = "Тепер вам потрібно вибрати одну або кілька областей, де ви хотіли б навчатись. Щоб скасувати вибір області, повторно натисніть на її кнопку"
    if "reg" in call.data.split():
        buttons = await nav.regions_buttons(callback="The end")
        await call.message.answer(text,
                                  reply_markup=buttons)
    elif "region" in call.data.split():
        buttons = await nav.regions_buttons(callback="finish")
        await call.message.edit_text(text,
                                     reply_markup=buttons)


@dp.callback_query_handler(text_contains="region")
async def add_or_remove_region(call: types.CallbackQuery):
    await call.answer()
    region_name = call.data.split()[1]
    await change_region(call, region_name)


@dp.callback_query_handler(text="finish")
async def list_region(call: types.CallbackQuery):
    await call.answer()
    await list_the_regions(call)


@dp.callback_query_handler(text_contains="The end", state=None)
async def get_exams_result(call: types.CallbackQuery):
    await call.answer()
    if "repeat" not in call.data.split():
        await list_the_regions(call)
    await call.message.answer("Тепер нам потрібно дізнатись ваші результати НМТ, щоб вирахувати середній бал для вибраної спеціальності.")
    await call.message.answer("Введіть бал з української мови у 200-бальній шкалі")
    await ExamsMarks.ua.set()


@dp.message_handler(state=ExamsMarks.ua)
async def get_ua(message: types.Message, state=FSMContext):
    ua1 = message.text
    finita_la_comedia = False
    correct_ua = False
    try:
        if int(ua1) <= 100 or int(ua1) > 200:
            await message.answer("Неправильна оцінка. Результат екзамену не може бути меншим за 100 чи більшим за 200. Введіть оцінку ще раз")
            correct_ua = False
        else:
            correct_ua = True
    except ValueError:
        await message.answer("Неправильний тип даних. Потрібно вводити тільки число. Повторіть спробу")
        finita_la_comedia = True
    if not finita_la_comedia and correct_ua:
        await state.update_data(ua=ua1, correct_ua=correct_ua)
        await message.answer("Введіть бал з математики у 200-бальній шкалі")
        await ExamsMarks.next()


@dp.message_handler(state=ExamsMarks.math)
async def get_math(message: types.Message, state=FSMContext):
    math1 = message.text
    finita_la_comedia = False
    correct_math = False
    try:
        if int(math1) <= 100 or int(math1) > 200:
            correct_math = False
            await message.answer("Неправильна оцінка. Результат екзамену не може бути меншим за 100 чи більшим за 200. Введіть оцінку ще раз")
        else:
            correct_math = True
    except ValueError:
        await message.answer("Неправильний тип даних. Потрібно вводити тільки число. Повторіть спробу")
        finita_la_comedia = True
    if not finita_la_comedia and correct_math:
        await state.update_data(math=math1, correct_math=correct_math)

        await message.answer("Введіть бал з історії у 200-бальній шкалі")
        await ExamsMarks.next()


@dp.message_handler(state=ExamsMarks.history)
async def get_history(message: types.Message, state=FSMContext):
    mark_history = int(message.text)
    finita_la_comedia = False
    correct = False
    try:
        if mark_history <= 100 or mark_history > 200:
            correct = False
            await message.answer("Неправильна оцінка. Результат екзамену не може бути меншим за 100 чи більшим за 200. Введіть оцінку ще раз")
        else:
            correct = True
    except ValueError:
        await message.answer("Неправильний тип даних. Потрібно вводити тільки число. Повторіть спробу")
        finita_la_comedia = True
    if not finita_la_comedia and correct:
        data = await state.get_data()
        mark_ua = int(data.get("ua"))
        mark_math = int(data.get("math"))
        db.users_specs.update_one({"user_id": message.from_user.id}, {"$set": {"marks": {"UA": mark_ua,
                                                                                         "Math": mark_math,
                                                                                         "History": mark_history}}})

        await message.answer(
                "Готово. Перевірте свої бали. Якщо все правильно, нажміть зберегти \n\n"
                f"Українська мова: {mark_ua},\n"
                f"Історія: {mark_history},\n"
                f"Математика: {mark_math}\n\n"
                "Якщо ви помилилися, нажміть кнопку", reply_markup=nav.save)
        await state.finish()


@dp.callback_query_handler(text="save")
async def save(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Налаштування завершено. Основні можливості бота представлено в команді /menu")


@dp.message_handler(lambda message: message.text == "Переглянути інформацію щодо спеціальностей")
async def average(message: types.Message):
    user_id = message.from_user.id
    user_data = db.users_specs.find_one({"user_id": user_id})
    await average_bal(message, user_data)


@dp.message_handler(commands="menu")
async def menu(message: types.Message):
    await message.answer("Меню бота. Для виклику функцій використовуйте кнопки. Якщо у вас раптом не видно кнопок, нажміть на квадратний значок з чотирма кружечками в ньому. Він є справа на полі вводу", reply_markup=nav.mainMenu)


@dp.message_handler(lambda message: message.text == "Змінити дані")
async def change_menu(message: types.Message):
    await message.answer("Оберіть, яку саме інформацію ви бажаєте виправити", reply_markup=nav.change_menu)


@dp.message_handler(lambda message: message.text == "Пошук університету", state=None)
async def search_uni(message: types.Message):
    await message.answer("Введіть назву навчального закладу. Деякі університети як ЛНУ ім. І.Франка не вдасться знайти за абревіатурою. "
                         "Ви можете спробувати, але якщо пошук нічого не видасть, університет не надав нам своєї абревіатури\n"
                         "Якщо ви випадково викликали функцію, введіть \"закінчити\"")
    await SearchUniver.name.set()


@dp.message_handler(state=SearchUniver.name)
async def find_univer(message: types.Message, state=FSMContext):
    if message.text.lower() == "закінчити":
        await message.answer("Роботу припинено")
        await state.finish()
    elif not message.text.lower() == "закінчити":
        array1 = message.text.split()
        await search(message, array1)
        await state.finish()


@dp.callback_query_handler(text_contains="append")
async def append_univer(call: types.CallbackQuery):
    await call.answer()
    code = call.data.split()[1]
    await ap_univer(call, code)


@dp.message_handler(lambda message: message.text == "Місце в рейтингу")
async def users_rating(message: types.Message):
    user_id = message.from_user.id
    try:
        user = db.users_specs.find_one({"user_id": user_id})
        first = user['first_name']
        try:
            specs = user['spec_codes']
            if len(specs) == 0:
                await message.answer("Для цієї функції потрібно вказати спеціальність, на яку ви подавали документи. Натисніть відповідну кнопку", reply_markup=nav.change_menu)
            else:
                await user_position(message, user)
        except KeyError:
            await message.answer("Для цієї функції потрібно вказати спеціальність, на яку ви подавали документи. Натисніть відповідну кнопку", reply_markup=nav.change_menu)
    except KeyError:
        await FirstName.first_name.set()
        await message.answer("Щоб скористатись цією функцію, вкажіть своє прізвище наступним повідомленням")


@dp.callback_query_handler(text="first_name", state=None)
async def change_first_name(call: types.CallbackQuery):
    await call.answer()
    await FirstName.first_name.set()
    await call.message.answer("Зміна прізвища. Введіть інформацію")


@dp.message_handler(state=FirstName.first_name)
async def set_first_name(message: types.Message, state=FSMContext):
    await set_fn(message)
    await message.answer("Прізвище внесено до бази даних.")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
