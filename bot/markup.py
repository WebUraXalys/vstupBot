from aiogram import types
from bson import ObjectId

from config import db

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

end = types.ReplyKeyboardMarkup(resize_keyboard=True)
end.add("Завершити обирати")


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

fix = types.InlineKeyboardMarkup()
fix.add(types.InlineKeyboardButton(text="Виправити помилку", callback_data="The end repeat"))

mainMenu = types.InlineKeyboardMarkup()
mainMenu.add(types.InlineKeyboardButton(text="Звіт по обраних спеціальностях та регіонах", callback_data="average"),
             types.InlineKeyboardMarkup(text="Пошук університету", callback_data="search"))


# ----------------------------------------------------------------------------------------------------------------------
# Кнопки для роботи зі спеціальностями
async def add_buttons():
    categories = db.categories_spec.find()
    categoriesMenu = types.InlineKeyboardMarkup()
    buttons = []
    for category in categories:
        name = category['categories_name']
        category_name = "category " + str(category['_id'])
        button = types.InlineKeyboardButton(text=name, callback_data=category_name)
        buttons.append(button)
    categoriesMenu.add(*buttons)
    return categoriesMenu


async def add_specs(category_id, page):
    specMenu = types.InlineKeyboardMarkup()
    category_find = db.categories_spec.find_one({"_id": ObjectId(category_id)})
    buttons = []
    number = len(category_find['spec_array'])
    if number > 23:
        num_of_codes = int(number/2)
        if page == "1":
            for spec in category_find['spec_array'][:num_of_codes]:
                spec_code = spec
                finder = db.specs.find_one({'name': {"$regex": spec_code}}, {'_id': 0, "name": 1})
                spec_name = "spec " + str(spec_code)
                button = types.InlineKeyboardButton(text=finder['name'], callback_data=spec_name)
                buttons.append(button)
            specMenu.row(types.InlineKeyboardButton(text="Наступна сторінка", callback_data=f"category {category_id} 2"))
        elif page == "2":
            for spec in category_find['spec_array'][num_of_codes:]:
                spec_code = spec
                finder = db.specs.find_one({'name': {"$regex": spec_code}}, {'_id': 0, "name": 1})
                spec_name = "spec " + str(spec_code)
                button = types.InlineKeyboardButton(text=finder['name'], callback_data=spec_name)
                buttons.append(button)
            specMenu.row(types.InlineKeyboardButton(text="Попередня сторінка", callback_data=f"category {category_id} 1"))

    else:
        for spec in category_find['spec_array']:
            spec_code = spec
            finder = db.specs.find_one({'name': {"$regex": spec_code}}, {'_id': 0, "name": 1})
            spec_name = "spec " + str(spec_code)
            button = types.InlineKeyboardButton(text=finder['name'], callback_data=spec_name)
            buttons.append(button)
    specMenu.add(*buttons)
    specMenu.row(types.InlineKeyboardButton(text="Повернутись", callback_data="спеціальність"))
    return specMenu


univerMarkup = types.InlineKeyboardMarkup()
