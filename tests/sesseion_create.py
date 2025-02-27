import asyncio
import logging
from contextlib import asynccontextmanager

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError

# Импортируем модели (предполагается, что они в database/models.py)
from app.database.models import Base, User

logging.basicConfig(level=logging.INFO)

# --- Database Configuration ---
DB_TYPE = "sqlite"  # or "mysql", "postgresql"
SQLITE_FILE = "bot.db"  # Путь к файлу базы данных
# --- MySQL or PostgreSQL ---
DB_HOST = "your_db_host"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_NAME = "your_db_name"

if DB_TYPE == "mysql":
    DATABASE_URL = f'mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
elif DB_TYPE == "postgresql":
    DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
elif DB_TYPE == "sqlite":
    DATABASE_URL = f'sqlite+aiosqlite:///{SQLITE_FILE}'
else:
    raise ValueError("Некорректное значение DB_TYPE. Используйте 'mysql' или 'sqlite'.")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_async_session():
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def test_connection():
    try:
        async with get_async_session() as session:
            print("Successfully connected to the database and created a session!")
    except Exception as e:
        print(f"Error connecting to the database: {e}")

async def main():
    await test_connection()

if __name__ == "__main__":
    asyncio.run(main())
