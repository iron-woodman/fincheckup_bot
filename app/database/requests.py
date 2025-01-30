from sqlalchemy import select, update, delete
from app.database.models2 import User
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


async def create_user(telegram_id, username, session: AsyncSession):
    """Создает нового пользователя."""
    user = User(tg_id=telegram_id)
    session.add(user)
    await session.commit()


async def get_user_by_telegram_id(telegram_id, session: AsyncSession):
    """Получает пользователя по telegram_id."""
    try:
        query = select(User).where(User.tg_id == telegram_id)
        print(query)
        result = await session.execute(query)
        user = result.scalar_one()
        return user
    except NoResultFound:
        return None


async def set_admin_status(telegram_id, is_admin, session: AsyncSession):
    """Устанавливает статус администратора для пользователя."""
    query = update(User).where(User.telegram_id == telegram_id).values(is_admin=is_admin)
    await session.execute(query)
    await session.commit()

async def get_all_users(session: AsyncSession):
    """Получает всех пользователей."""
    query = select(User)
    result = await session.execute(query)
    users = result.scalars().all()
    return users

async def delete_user(telegram_id, session: AsyncSession):
    """Удаляет пользователя по telegram_id."""
    query = delete(User).where(User.tg_id == telegram_id)
    await session.execute(query)
    await session.commit()

async def clear_table(session: AsyncSession):
    """Очищает таблицу пользователей"""
    query = text("DELETE FROM users")
    await session.execute(query)
    await session.commit()


async def get_count_users(session: AsyncSession):
    """Получает кол-во всех пользователей"""
    query = select(User)
    result = await session.execute(query)
    return len(result.scalars().all())

async def get_all_admin(session: AsyncSession):
    """Получает всех админов."""
    query = select(User).where(User.is_admin == True)
    result = await session.execute(query)
    admins = result.scalars().all()
    return admins
