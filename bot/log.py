import time
from config import bot


async def log_call(call, start_time):
    end_time = time.time() - start_time
    username = call.from_user.username
    callback = call.data
    await bot.send_message(chat_id="-662497110",
                           text=f"Лог виклику\n"
                                f"Нікнейм користувача: {username}\n"
                                f"Дані виклику: {callback}\n"
                                f"Час виконання: {end_time}\n")


async def log_message(message, start_time):
    end_time = time.time() - start_time
    username = message.from_user.username
    command = message.text

    await bot.send_message(chat_id="-662497110",
                           text=f"Лог виклику\n"
                                f"Нікнейм користувача: {username}\n"
                                f"Введена інформація/команда: {command}\n"
                                f"Час виконання: {end_time}\n")
