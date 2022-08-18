from aiogram import types
from bson import ObjectId

from config import db

guideMenu = types.InlineKeyboardMarkup(row_width=2)
guideMenu.add(types.InlineKeyboardButton(text="Текстовий гайд", url="google.com", callback_data="trusted"),
              types.InlineKeyboardButton(text="Відео гайд", url="youtube.com", callback_data="trusted"))


continueMenu = types.InlineKeyboardMarkup(row_width=2)
continueMenu.add(types.InlineKeyboardButton(text="Так", callback_data="yes"),
                 types.InlineKeyboardButton(text="Ні", callback_data="no"))


check_profession = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
buttons = ["Так", "Ні"]
check_profession.add(*buttons)


check_profession_step_2 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
check = ["Так", "Ще ні"]
check_profession_step_2.add(*check)


specialization = types.InlineKeyboardMarkup()
specBTN = [types.InlineKeyboardButton(text="Ввести код", callback_data="код"),
           types.InlineKeyboardButton(text="Спеціальність", callback_data="спеціальність")]
specialization.add(*specBTN)


cont = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cont.add("Продовжити далі")

end = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
end.add("Завершити обирати")


async def regions_buttons(callback):
    regions = db.regions.find()
    regions_markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for region in regions:
        name = region['name']
        callback_data = "region " + region['name']
        button = types.InlineKeyboardButton(text=name, callback_data=callback_data)
        buttons.append(button)
    buttons.append(types.InlineKeyboardButton(text="Завершити обирати", callback_data=callback))
    regions_markup.add(*buttons)
    return regions_markup


save = types.InlineKeyboardMarkup()
save.add(types.InlineKeyboardButton(text="Зберегти", callback_data="save"), types.InlineKeyboardButton(text="Виправити помилку", callback_data="The end repeat"))


mainMenu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
mainMenu.add("Змінити дані", "Пошук університету", "Переглянути мої спеціальності")
mainMenu.row("Місце в рейтингу")

change_menu = types.InlineKeyboardMarkup(row_width=2)
change_menu.add(types.InlineKeyboardButton(text="Спеціальність", callback_data="спеціальність"),
                types.InlineKeyboardButton(text="Регіон", callback_data="change region"),
                types.InlineKeyboardButton(text="Бали", callback_data="The end repeat"),
                types.InlineKeyboardButton(text="Прізвище", callback_data="first_name"))


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
    categoriesMenu.row(types.InlineKeyboardButton(text="Зберегти спеціальності", callback_data="change reg"))
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


async def univer(elem):
    navigation = types.InlineKeyboardMarkup()
    navigation.add(types.InlineKeyboardButton(text="Додати в обрані", callback_data=f"append {elem['code']}"))
    return navigation
