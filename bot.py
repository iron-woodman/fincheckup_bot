import asyncio
from aiogram import Bot, Dispatcher

from app.config import BOT_TOKEN
from app.handlers.handlers import router
from app.handlers.reg_user_handlers import register_router
from app.database.models2 import async_main
from app.middlewares.db_session import DBSessionMiddleware


async def main():
    await async_main() # создаем таблицы БД (если они не сущестовали ранее)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(register_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен.')
