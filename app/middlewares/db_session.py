from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_async_session  # Import your generator function
from contextlib import asynccontextmanager


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        @asynccontextmanager
        async def session_manager():
            async for session in get_async_session():
                yield session


        try:
            async with session_manager() as session:
                data["session"] = session
                return await handler(event, data)
        except Exception as e:
            raise e

