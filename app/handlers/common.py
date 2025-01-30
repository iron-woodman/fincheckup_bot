from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from app.database.requests import get_user_by_telegram_id, create_user, set_admin_status
from app.config import ADMIN_IDS
from sqlalchemy.ext.asyncio import AsyncSession
import app.keyboards.user_keyboards as user_kb

common_router = Router()


@common_router.message(CommandStart())
async def start_handler(message: types.Message, session: AsyncSession):
    """Обработчик команды /start, асинхронный."""
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    user = await get_user_by_telegram_id(user_id, session) # используем await
    if not user:
        await create_user(user_id, username, session)  # используем await
        await message.answer(f"Привет, {full_name}! Вы зарегистрированы.")
        if user_id in ADMIN_IDS:
            await set_admin_status(user_id, True, session)  # используем await
    else:
        await message.answer(f"Снова привет, {full_name}!", reply_markup=user_kb.start_test)


@common_router.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer("Этот бот поможет вам ...")
