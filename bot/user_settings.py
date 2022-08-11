import asyncio

from config import db
import markup as nav


async def change_spec(call, spec_code):
    user_id = call.from_user.id
    user = db.users_specs.find_one({"user_id": user_id})
    if user is None:
        db.users_specs.insert_one({'user_id': user_id,
                                   'spec_codes': [spec_code],
                                   'UA': "",
                                   'Math': "",
                                   "History": ""})
        await call.message.answer("Запис внесено до бази даних")
        await call.message.answer(f"Вибрано спеціальність: {spec_code}", reply_markup=nav.end)
    else:
        try:
            if spec_code in user['spec_codes']:
                db.users_specs.update_one({'user_id': user_id}, {'$pull': {'spec_codes': spec_code}})
                await call.message.answer(f"Видалено спеціальність: {spec_code}", reply_markup=nav.end)
            else:
                db.users_specs.update_one({'user_id': user_id}, {'$push': {'spec_codes': spec_code}})
                await call.message.answer(f"Вибрано спеціальність: {spec_code}", reply_markup=nav.end)
        except KeyError:
            db.users_specs.update_one({'user_id': user_id}, {'$push': {'spec_codes': spec_code}})
            await call.message.answer(f"Вибрано спеціальність: {spec_code}", reply_markup=nav.end)


async def massive_change_spec(message, list_of_spec):
    user_id = message.from_user.id
    spec_codes = []

    for value in list_of_spec[1::]:
        # Code checks does specialization exist and add it to list of chosen ones
        finder = list(db.specs.find({'name': {"$regex": value}}, {'_id': 0, "name": 1}))
        if len(finder) >= 1:
            spec_codes.append(value)
        elif len(finder) < 1:
            await message.reply(f"Такої спеціальності нема: {value}")

    # Work with database. Firstly we check does user exist in our db.
    # Then we create or update document in collection. It depends on result from previous step
    res = db.users_specs.find_one({'user_id': user_id})
    if res is None:
        db.users_specs.insert_one({'user_id': user_id,
                                   'spec_codes': spec_codes,
                                   'UA': "",
                                   'Math': "",
                                   "History": ""})
        await message.answer("Запис внесено до бази даних")
        await message.answer(f"Вибрано спеціальності: {spec_codes}", reply_markup=nav.cont)
    else:
        db.users_specs.update_one({'user_id': user_id}, {'$set': {'spec_codes': spec_codes}})
        await message.answer("Запис в базі даних оновлено")
        await message.answer(f"Вибрано спеціальності: {spec_codes}", reply_markup=nav.cont)


async def change_region(call, region_name):
    user_id = call.from_user.id
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
    except TypeError:
        db.users_specs.insert_one({'user_id': user_id,
                                   "region": [region_name]})
        if region_name == "Київ" or region_name == "АР Крим":
            await call.message.answer(f"Додано регіон: {region_name}")
        else:
            await call.message.answer(f"Додано регіон: {region_name} область")


async def list_the_regions(call):
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


async def average_bal(call, user_data):
    spec_codes = user_data["spec_codes"]
    regions = []

    for item in user_data["region"]:
        if item == "Київ":
            regions.append("КИЇВ")
        elif item == "АР Крим":
            pass
        else:
            regions.append(item + " область")

    for region in regions:
        for spec_item in spec_codes:
            find_univ = db.univs.find({"region": region, "specs": {"$elemMatch": {"spec_code": spec_item}}})
            for objection in find_univ:
                for spec in objection['specs']:
                    if spec['spec_code'] in spec_codes:
                        ua_koef = 0
                        math_koef = 0
                        history_koef = 0
                        for exam_requirement in spec['contest_subjects']:
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
                                                      f"Спеціальність: {spec['spec_name']} {spec['spec_code']}\n"
                                                      f"Код закладу: {objection['code']}\n\n"
                                                      f"<b>Статистика закладу</b>\n"
                                                      f"Загальна кількість місць:{spec['stat']['statm_all_count']}\n"
                                                      f"З них бюджет:{spec['stat']['statm_budget']}\n"
                                                      f"Подано заяв:{spec['stat']['statm_admitted']}\n"
                                                      f"Максимальний бал: {spec['stat']['mark_max']}\n"
                                                      f"Середній бал: {spec['stat']['mark_avg']}\n"
                                                      f"Мінімальний бал: {spec['stat']['mark_min']}\n"
                                                      f"Ваш середній бал:{average_enjoyer}\n", parse_mode="HTML", disable_notification=True)
                            await asyncio.sleep(1)
                        except KeyError:
                            await call.message.answer(f"Назва університету: {objection['name']}\n"
                                                      f"Регіон: {objection['region']}\n"
                                                      f"Спеціальність: {spec['spec_name']} {spec['spec_code']}\n"
                                                      f"Код закладу: {objection['code']}\n\n"
                                                      f"Заклад не надав статистику\n"
                                                      f"Ваш середній бал:{average_enjoyer}\n", disable_notification=True)
                            await asyncio.sleep(1)
