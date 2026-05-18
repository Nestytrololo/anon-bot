import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not found")

CHAT_ID = -1003942696028
TOPIC_ID = 117

bot = Bot(token=TOKEN)
dp = Dispatcher()

mode_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Анонимно"),
            KeyboardButton(text="С ником"),
        ]
    ],
    resize_keyboard=True,
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить"),
            KeyboardButton(text="Отмена"),
        ]
    ],
    resize_keyboard=True,
)

user_modes = {}
pending_messages = {}


@dp.message(CommandStart())
async def start(message: types.Message):
    if message.chat.type != "private":
        return

    await message.answer(
        "Выбери режим.",
        reply_markup=mode_keyboard,
    )


@dp.message()
async def handle_message(message: types.Message):
    if message.chat.type != "private":
        return

    if message.from_user and message.from_user.is_bot:
        return

    if not message.text:
        await message.answer("Пока я принимаю только текстовые сообщения.")
        return

    user_id = message.from_user.id

    if message.text in ["Анонимно", "С ником"]:
        user_modes[user_id] = message.text
        pending_messages.pop(user_id, None)
        await message.answer("Теперь напиши сообщение.")
        return

    if message.text == "Отмена":
        pending_messages.pop(user_id, None)
        await message.answer("Отменено.", reply_markup=mode_keyboard)
        return

    if message.text == "Отправить":
        text = pending_messages.pop(user_id, None)

        if not text:
            await message.answer(
                "Нет сообщения для отправки.",
                reply_markup=mode_keyboard,
            )
            return

        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                message_thread_id=TOPIC_ID,
                text=text,
            )
            await message.answer("Отправлено.", reply_markup=mode_keyboard)
            print("Message sent to confession topic", flush=True)
        except Exception as e:
            print("SEND ERROR:", e, flush=True)
            await message.answer(
                "Не получилось отправить сообщение. Проверь права бота.",
                reply_markup=mode_keyboard,
            )
        return

    mode = user_modes.get(user_id, "Анонимно")

    if mode == "С ником":
        username = message.from_user.username or message.from_user.first_name or "user"
        text = f"💬 @{username}:\n\n{message.text}"
    else:
        text = f"💬 Аноним:\n\n{message.text}"

    pending_messages[user_id] = text

    await message.answer(
        "Сообщение подготовлено. Нажми «Отправить», если всё правильно.",
        reply_markup=confirm_keyboard,
    )


async def main():
    print("BOT STARTED", flush=True)

    await bot.delete_webhook(drop_pending_updates=True)

    me = await bot.get_me()
    print("Connected as:", me.username, flush=True)

    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
