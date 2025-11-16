# --------------------------------------------------------------------------------
# Модуль обработки команд из приватных чатов
# --------------------------------------------------------------------------------
# Импорты
# --------------------------------------------------------------------------------


import os

from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from openai import OpenAI, OpenAIError, RateLimitError, PermissionDeniedError


from kbds.reply import get_keyboard


# --------------------------------------------------------------------------------
# Настройки
# --------------------------------------------------------------------------------


user_private_router = Router()

openai_key = os.getenv("OPENAI_KEY")

messages = [{"role": "system", "content": "You are helpful chat gpt bot in telegram"}]


# --------------------------------------------------------------------------------
# Клавиатуры
# --------------------------------------------------------------------------------


START_KB = get_keyboard(
    "Новый запрос",
    sizes=(1,),
)


# --------------------------------------------------------------------------------
# FSM состояния
# --------------------------------------------------------------------------------


class ChatContextState(StatesGroup):
    context = State()


# --------------------------------------------------------------------------------
# Базовый контекст
# --------------------------------------------------------------------------------


def default_context():
    return [
        {"role": "system", "content": "You are helpful ChatGPT bot in Telegram"}
    ]


# --------------------------------------------------------------------------------
# Обработчики
# --------------------------------------------------------------------------------


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.update_data(context=default_context())
    await message.answer("Привет! Я Telegram бот в который интегрирован ChatGPT. Введи сообщение", reply_markup=START_KB)


@user_private_router.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "/start - запускает бота и обнуляет контекст gpt\n"
        "/help - выводит список возможностей бота и их описание\n"
        "Напиши мне любой текст, и я на него отвечу")


@user_private_router.message(F.text.lower() == 'новый запрос')
async def new_request_cmd(message: types.Message, state: FSMContext):
    await state.update_data(context=default_context())
    await message.answer("Я всё забыл. Жду новый запрос")


# --------------------------------------------------------------------------------
# Главный обработчик
# --------------------------------------------------------------------------------


@user_private_router.message(F.text)
async def gpt_request(message: types.Message, state: FSMContext):
    # Получаем контекст пользователя
    data = await state.get_data()
    context = data.get("context", default_context())

    # Добавляем сообщение пользователя в контекст
    context.append({"role": "user", "content": message.text})

    try:
        client = OpenAI(
           base_url="https://neuroapi.host/v1",
           api_key=openai_key,
        )

        response = client.responses.create(
            model="gpt-4o-mini",
            input=context,
            store=True,
        )

        answer = response.output_text

        # Добавляем ответ ассистента в контекст
        context.append({"role": "assistant", "content": answer})

        # Сохраняем обновлённый контекст
        await state.update_data(context=context)

        # Отправляем ответ пользователю
        await message.answer(answer)

    except RateLimitError:
        # Ошибка: закончилась квота / тариф не оплачен
        await message.answer(
            "Похоже, что квота на использование ChatGPT закончилась или тариф не оплачен.\n"
            "Пожалуйста, продлите доступ в панели OpenAI и попробуйте снова."
        )


    except PermissionDeniedError:
        # Ошибка: доступ к модели запрещён (тоже бывает при неоплате)
        await message.answer(
            "У API-ключа недостаточно прав для обращения к модели.\n"
            "Возможно, тариф не оплачен или закончилась квота."
        )


    except OpenAIError:
        await message.answer(
            "Извините, сервис ChatGPT временно недоступен. Попробуйте позже."
        )
    

@user_private_router.message()
async def gpt_request_invalid(message: types.Message):
    await message.answer("Бот работает только с текстовыми сообщениями")









