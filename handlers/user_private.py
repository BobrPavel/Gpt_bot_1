# Модуль обработки команд из приватных чатов

from aiogram import types, Router
from aiogram.filters import CommandStart, Command


from kbds import reply

user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет я Telegram бот, который интегрирован с ChatGPT. Введите свой запрос", reply_markup=reply.start_kb
    )

@user_private_router.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        '''/start - запускает бота и обнуляет контекст gpt 
/help - выводит список возможностей бота и их описание 
Что бы отправить запрос в ИИ, просто введите сообщение''')





    