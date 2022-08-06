from aiogram import types

guideBTN = [
        types.InlineKeyboardButton(text="Текстовий гайд", url="google.com", callback_data="trusted"),
        types.InlineKeyboardButton(text="Відео гайд", url="youtube.com", callback_data="trusted"),
    ]
guideMenu = types.InlineKeyboardMarkup(row_width=2)
guideMenu.add(*guideBTN)


continueBTN = [
        types.InlineKeyboardButton(text="Так", callback_data="yes"),
        types.InlineKeyboardButton(text="Ні", callback_data="no"),
    ]
continueMenu = types.InlineKeyboardMarkup(row_width=2)
continueMenu.add(*continueBTN)


check_profession = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = ["Так", "Ні"]
check_profession.add(*buttons)


check_profession_step_2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
check = ["Так", "Ще ні"]
check_profession_step_2.add(*check)


specialization = types.InlineKeyboardMarkup()
specBTN = [types.InlineKeyboardButton(text="Ввести код", callback_data="код"),
           types.InlineKeyboardButton(text="Спеціальність", callback_data="спеціальність")]
specialization.add(*specBTN)


cont = types.ReplyKeyboardMarkup(resize_keyboard=True)
cont.add("Продовжити далі")


regions = types.InlineKeyboardMarkup(row_width=2)
regionBTN = [types.InlineKeyboardButton(text="АР Крим", callback_data="region АР Крим"),
             types.InlineKeyboardButton(text="Вінницька", callback_data="region Вінницька"),
             types.InlineKeyboardButton(text="Волинська", callback_data="region Волинська"),
             types.InlineKeyboardButton(text="Дніпропетровська", callback_data="region Дніпропетровська"),
             types.InlineKeyboardButton(text="Донецька", callback_data="region Донецька"),
             types.InlineKeyboardButton(text="Житомирська", callback_data="region Житомирська"),
             types.InlineKeyboardButton(text="Закарпатська", callback_data="region Закарпатська"),
             types.InlineKeyboardButton(text="Івано-Франківська", callback_data="region Івано-Франківська"),
             types.InlineKeyboardButton(text="Київська", callback_data="region Київська"),
             types.InlineKeyboardButton(text="Кіровоградська", callback_data="region Кіровоградська"),
             types.InlineKeyboardButton(text="Луганська", callback_data="region Луганська"),
             types.InlineKeyboardButton(text="Львівська", callback_data="region Львівська"),
             types.InlineKeyboardButton(text="Миколаївська", callback_data="region Миколаївська"),
             types.InlineKeyboardButton(text="Одеська", callback_data="region Одеська"),
             types.InlineKeyboardButton(text="Полтавська", callback_data="region Полтавська"),
             types.InlineKeyboardButton(text="Рівненська", callback_data="region Рівненська"),
             types.InlineKeyboardButton(text="Сумська", callback_data="region Сумська"),
             types.InlineKeyboardButton(text="Тернопільська", callback_data="region Тернопільська"),
             types.InlineKeyboardButton(text="Харківська", callback_data="region Харківська"),
             types.InlineKeyboardButton(text="Херсонська", callback_data="region Херсонська"),
             types.InlineKeyboardButton(text="Хмельницька", callback_data="region Хмельницька"),
             types.InlineKeyboardButton(text="Черкаська", callback_data="region Черкаська"),
             types.InlineKeyboardButton(text="Чернівецька", callback_data="region Чернівецька"),
             types.InlineKeyboardButton(text="Чернігівська", callback_data="region Чернігівська"),
             types.InlineKeyboardButton(text="Київ", callback_data="region Київ"),
             types.InlineKeyboardButton(text="Завершити обирати регіон", callback_data="The end"),
             ]
regions.add(*regionBTN)

save = types.InlineKeyboardMarkup()
save.add(types.InlineKeyboardButton(text="Зберегти", callback_data="save"), types.InlineKeyboardButton(text="Виправити помилку", callback_data="The end repeat"))
