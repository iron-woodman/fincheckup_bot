import asyncio
import logging
from typing import List, Dict, Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import get_async_session
from app.database.models import User, UserAnswerOptions, AnswerOption, Question
from app.database.requests2 import get_user_answers
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)




# Пример использования:
async def main():
    user_telegram_id = 980992117  # Замени на реальный telegram_id
    user_answers = await get_user_answers(user_telegram_id)

    if user_answers:
        print(f"Ответы пользователя с telegram_id {user_telegram_id}:")
        for answer in user_answers:
            print(answer)
    else:
        print(f"Ответы для пользователя с telegram_id {user_telegram_id} не найдены.")

if __name__ == "__main__":
    asyncio.run(main())
