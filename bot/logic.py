import asyncio
from config import db


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


async def average_bal(message, user_data):
    spec_codes = user_data["spec_codes"]
    regions = []

    for item in user_data["region"]:
        obj = db.regions.find_one({"name": item})
        region_name = obj['spec_name']
        regions.append(region_name)

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
                        average_enjoyer = int(user_data['UA']) * ua_koef + int(user_data['Math']) * math_koef + int(
                            user_data['History']) * history_koef
                        try:
                            await message.answer(f"Назва університету: {objection['name']}\n"
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
                                                 f"Ваш середній бал:{average_enjoyer}\n", parse_mode="HTML",
                                                 disable_notification=True)
                            await asyncio.sleep(1)
                        except KeyError:
                            await message.answer(f"Назва університету: {objection['name']}\n"
                                                 f"Регіон: {objection['region']}\n"
                                                 f"Спеціальність: {spec['spec_name']} {spec['spec_code']}\n"
                                                 f"Код закладу: {objection['code']}\n\n"
                                                 f"Заклад не надав статистику\n"
                                                 f"Ваш середній бал:{average_enjoyer}\n", disable_notification=True)
                            await asyncio.sleep(1)


async def user_position(message, user):
    for univer_code in user['universities']:
        univer_list = db.univs.find({'code': univer_code})
        for univer in univer_list:
            for spec in univer['specs']:
                if spec['spec_code'] in user['spec_codes']:
                    for human in spec['rqs']:
                        full_name = human['fio']
                        if user['first_name'] in full_name.split():
                            await message.answer(f"Університет: {univer['name']}\n"
                                                 f"Факультет: {spec['fac_name']}\n"
                                                 f"Спеціальність: {spec['spec_name']}\n"
                                                 f"Загальна кількість місць: {spec['licenses_count']}\n"
                                                 f"З них державних: {spec['max_gov_order_count']}\n\n"
                                                 f"Подано заявок: {spec['stat']['statm_all_count']}\n"
                                                 f"З них на бюджет: {spec['stat']['statm_budget']}\n"
                                                 f"Ваше місце в списку: {human['n']}")
