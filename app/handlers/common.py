from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from app.database.requests import add_user, get_user_by_telegram_id
from app.config import ADMIN_IDS
import app.keyboards.user_keyboards as user_kb
import app.keyboards.admin_keyboards as admin_kb

common_router = Router()


async def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@common_router.message(CommandStart())
async def start_handler(message: types.Message):
    """Обработчик команды /start, асинхронный."""
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    print('tld id = ', user_id)

    if await is_admin(user_id):
        # админ
        await message.reply("Привет, админ!", reply_markup=admin_kb.admin_keyboard)
    else:
        # user
        user = await get_user_by_telegram_id(user_id) # используем await
        if not user:
            await add_user(user_id)
            await message.answer(f"""
            Привет!\nЯ твой цифровой ассистент FinCheckUp на пути к твоим целям. Пройдите небольшой отпрос.
    📌 Это займет всего 3 минуты!
     """, reply_markup=user_kb.start_test)
            # if user_id in ADMIN_IDS:
            #     await set_admin_status(user_id, True, session)  # используем await
        else:
            await message.answer(f"""
            Привет!\nЯ твой цифровой ассистент FinCheckUp на пути к твоим целям. Пройдите небольшой отпрос.
    📌 Это займет всего 3 минуты!
     """, reply_markup=user_kb.start_test)


@common_router.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer("Этот бот поможет вам ...")
