import asyncio
from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from contextlib import asynccontextmanager

from app.database.database import get_async_session
from app.database.models2 import User, UserProfile, MarriageStatus


logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def session_manager():
    async for session in get_async_session():
        yield session


async def set_user(tg_id: int) -> bool:
    """
    Регистрация нового пользователя бота (заносим его телеграм ID)
    :param tg_id:
    :return: True если пользователь был добавлен, False если он уже существует
    """
    async with session_manager() as session:
        try:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                session.add(User(telegram_id=tg_id))
                await session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logging.error(f"Error setting user: {e}")
            await session.rollback()
            return False


async def add_new_user_profile(
    tg_id: int,
    first_name: str = None,
    last_name: str = None,
    birth_date: date = None,
    marriage_status: MarriageStatus = None,
    phone_number: str = None,
    email: str = None,
    children_under_18: int = None,
) -> bool:
    """
    Добавляем новый профиль пользователя в БД
    :param tg_id:
    :param first_name:
    :param last_name:
    :param birth_date:
    :param marriage_status:
    :param phone_number:
    :param email:
    :param children_under_18:
    :return: True если профиль был добавлен, False если произошла ошибка
    """
    async with session_manager() as session:
        try:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                user = User(telegram_id=tg_id)
                session.add(user)
                await session.commit()  # commit first to get the id
                user = await session.scalar(select(User).where(User.tg_id == tg_id)) # повторный запрос для получения id

            user_profile = UserProfile(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                marriage_status=marriage_status,
                phone_number=phone_number,
                email=email,
                children_under_18=children_under_18,
            )
            session.add(user_profile)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            logging.error(f"Error adding user profile: {e}")
            await session.rollback()
            return False


async def main():
    # Пример использования:
    registration_data = {
        "tg_id": 123456789,
        "first_name": "John",
        "last_name": "Doe",
        "birth_date": date(1990, 5, 15),
        "marriage_status": MarriageStatus.VERHEIRATET,
        "phone_number": "+1234567890",
        "email": "john.doe@example.com",  # Используйте "email" вместо "waiting_for_email"
        "children_under_18": 2,
    }
    try:
        success = await add_new_user_profile(**registration_data)
        if success:
            print("User profile added successfully.")
        else:
            print("Failed to add user profile.")
    except Exception as e:
         logging.error(f"Ошибка добавления профиля пользователя {e}")

    # Пример использования без всех данных
    registration_data = {
        "tg_id": 987654321,
    }
    try:
        success = await add_new_user_profile(**registration_data)
        if success:
            print("User profile added successfully.")
        else:
            print("Failed to add user profile.")
    except Exception as e:
         logging.error(f"Ошибка добавления профиля пользователя {e}")


if __name__ == "__main__":
    asyncio.run(main())
