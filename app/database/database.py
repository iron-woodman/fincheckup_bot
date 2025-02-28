## -*- coding: utf-8 -*-

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_TYPE, SQLITE_FILE
from app.database.models import Base
from typing import AsyncGenerator

# Перенесенное создание движка, чтобы его можно было использовать повторно
def create_async_engine_from_config():
    if DB_TYPE == "mysql":
        engine = create_async_engine(
            f'mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}',
            echo=True,  # Включим логирование запросов для дебага
        )
    elif DB_TYPE == "sqlite":
        engine = create_async_engine(
            f'sqlite+aiosqlite:///{SQLITE_FILE}',
            echo=True, # Включим логирование запросов для дебага
        )
    else:
        raise ValueError("Некорректное значение DB_TYPE. Используйте 'mysql' или 'sqlite'.")
    return engine

# Создание движка
engine = create_async_engine_from_config()

# Создание SessionMaker для асинхронных сессий
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Функция для создания сессии
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
           await session.close()



async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def init_db():
    await create_tables()

if __name__ == '__main__':
   asyncio.run(init_db())
