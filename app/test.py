import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError


# Замените на вашу строку подключения к базе данных
DATABASE_URL = 'sqlite+aiosqlite:///db.sqlite3'



class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    category_id: Mapped[int] = mapped_column()

async_engine = create_async_engine(DATABASE_URL, echo=True)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncSession:
    async_session = AsyncSession(async_engine)
    return async_session


async def set_user(tg_id):
    async with await get_async_session() as session:
        try:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if not user:
                new_user = User(tg_id=tg_id)
                session.add(new_user)
                await session.flush()
                await session.commit()
                return new_user
            return user
        except SQLAlchemyError as e:
            print(f"Error during set_user: {e}")
            await session.rollback()
            return None # Или выбросить исключение, в зависимости от того, как ты хочешь обрабатывать ошибки.


async def get_categories():
    async with await get_async_session() as session:
        try:
            print("Start query categories")
            all_cat = await session.scalars(select(Category))
            categories = [category for category in all_cat]
            for category in categories:
                print(category.name)
            print("Finish query categories")
            return categories
        except SQLAlchemyError as e:
             print(f"Error during get_categories: {e}")
             return [] # Или выбросить исключение, в зависимости от того, как ты хочешь обрабатывать ошибки.


async def main():
     await init_db()
     # user = await set_user(123)
     # print(f"set user result: {user}")
     categories = await get_categories()
     print(f"get categories result: {categories}")


if __name__ == "__main__":
    asyncio.run(main())
