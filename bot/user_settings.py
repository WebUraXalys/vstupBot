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
        await call.message.answer(f"Вибрано спеціальність: {spec_code}")
    else:
        try:
            if spec_code in user['spec_codes']:
                db.users_specs.update_one({'user_id': user_id}, {'$pull': {'spec_codes': spec_code}})
                await call.message.answer(f"Видалено спеціальність: {spec_code}")
            else:
                db.users_specs.update_one({'user_id': user_id}, {'$push': {'spec_codes': spec_code}})
                await call.message.answer(f"Вибрано спеціальність: {spec_code}")
        except KeyError:
            db.users_specs.update_one({'user_id': user_id}, {'$push': {'spec_codes': spec_code}})
            await call.message.answer(f"Вибрано спеціальність: {spec_code}")


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

    res = db.users_specs.find_one({'user_id': user_id})
    try:
        if region_name not in res["region"]:
            print(region_name)
            db.users_specs.update_one({'user_id': user_id}, {"$push": {"region": region_name}})
            if region_name == "Київ":
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
        if region_name == "Київ":
            await call.message.answer(f"Додано регіон: {region_name}")
        else:
            await call.message.answer(f"Додано регіон: {region_name} область")
    except TypeError:
        db.users_specs.insert_one({'user_id': user_id,
                                   "region": [region_name]})
        if region_name == "Київ":
            await call.message.answer(f"Додано регіон: {region_name}")
        else:
            await call.message.answer(f"Додано регіон: {region_name} область")


async def ap_univer(call, code):
    user_id = call.from_user.id
    document = db.users_specs.find_one({"user_id": user_id})
    try:
        if code in document['universities']:
            db.users_specs.update_one({"user_id": user_id}, {"$pull": {"universities": code}})
        else:
            db.users_specs.update_one({"user_id": user_id}, {"$push": {"universities": code}})

    except KeyError:
        db.users_specs.update_one({"user_id": user_id}, {"$push": {"universities": code}})


async def set_fn(message):
    db.users_specs.update_one({"user_id": message.from_user.id}, {"$set": {'first_name': message.text}})
