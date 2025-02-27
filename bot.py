import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update  # Импортируем Update

from app.config import BOT_TOKEN
from app.middlewares.db_session import DBSessionMiddleware
from app.handlers.common import common_router
from app.handlers.user import user_router
from app.handlers.admin import admin_router
from app.handlers.admin_report import report_router
from app.handlers.user_test import user_test_router
from app.handlers.admin_db import db_router
from app.database.database import create_tables


# from app.handlers.admin import admin_router


async def main():
    # Настройка логирования (рекомендуется для отслеживания ошибок)
    logging.basicConfig(level=logging.INFO)

    # Создание таблиц базы данных (если они не существуют)
    try:
        await create_tables()
        # await add_question_data()
    except Exception as e:
        logging.error(f"Ошибка при создании таблиц БД: {e}")

    # Инициализация бота и хранилища состояний
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()  # Можно использовать RedisStorage2, если нужна персистентность
    dp = Dispatcher(storage=storage)

    # Регистрация middleware (нужно указать тип апдейта для middleware)
    dp.update.middleware(DBSessionMiddleware())

    # Регистрация роутеров
    dp.include_router(common_router)
    dp.include_router(user_router)
    dp.include_router(user_test_router)
    dp.include_router(admin_router)
    dp.include_router(report_router)
    dp.include_router(db_router)

    # Запуск поллинга
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        # Закрытие сессии бота
        try:
            await bot.session.close()
        except Exception as e:
            logging.error(f"Ошибка при закрытии сессии бота: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен.')
    except Exception as e:
        logging.error(f"Произошла ошибка при запуске бота: {e}")
