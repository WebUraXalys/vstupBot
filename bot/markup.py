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
