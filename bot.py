import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("BOT_TOKEN not found", flush=True)
    raise RuntimeError("BOT_TOKEN not found")

CHAT_ID = -1003942696028
TOPIC_ID = 117

bot = Bot(token=TOKEN)
dp = Dispatcher()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Анонимно"),
            KeyboardButton(text="С ником"),
        ]
    ],
    resize_keyboard=True,
)

user_modes = {}


@dp.message(CommandStart())
async def start(message: types.Message):
    print("START from user:", message.from_user.id, flush=True)
    await message.answer("Выбери режим", reply_markup=keyboard)


@dp.message()
async def handle_message(message: types.Message):
    print("New message:", message.text, flush=True)

    user_id = message.from_user.id

    if message.text in ["Анонимно", "С ником"]:
        user_modes[user_id] = message.text
        await message.answer("Теперь напиши сообщение")
        return

    mode = user_modes.get(user_id, "Анонимно")

    if mode == "С ником":
        username = message.from_user.username or message.from_user.first_name or "user"
        text = f"@{username}:\n\n{message.text}"
    else:
        text = f"Аноним:\n\n{message.text}"

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=TOPIC_ID,
            text=text,
        )
        await message.answer("Отправлено")
        print("Message sent to group", flush=True)
    except Exception as e:
        await message.answer("Не получилось отправить сообщение")
        print("SEND ERROR:", e, flush=True)


async def main():
    print("BOT STARTED", flush=True)

    me = await bot.get_me()
    print("Connected as:", me.username, flush=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
