from config import db


async def search(message, array_1):
    univers = db.univs.find({"short_name": {"$in": array_1}})
    list_of_univs = []
    for univer in univers:
        nem_of_words = 0
        for a in array_1:
            if a in univer['short_name']:
                nem_of_words += 1
        num_of_words = len(array_1)
        another_percents = nem_of_words/num_of_words
        list_of_univs.append({"percents": another_percents,
                              'univer': univer})

    list_of_univs.sort(key=lambda item: item.get("percents"))
    for elem in list_of_univs:
        if elem['percents'] >= 0.35:
            await message.answer("Інформація щодо університету\n"
                                 f"Назва: {elem['univer']['name']}\n"
                                 f"Регіон: {elem['univer']['region']}")
