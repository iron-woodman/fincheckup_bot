import asyncio
from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from app.database.database import get_async_session
from app.database.models import User, UserProfile, Question, AnswerOption, Answer

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def session_manager():
    async for session in get_async_session():
        yield session


async def get_user_by_telegram_id(tg_id):
    """Получает пользователя по telegram_id."""
    async with session_manager() as session:
        try:
            user = await session.scalar(select(User).where(User.telegram_id == tg_id))
            return user
            # if not user:
            #     session.add(User(telegram_id=tg_id))
            #     await session.commit()
            #     return True
            # return False
        except SQLAlchemyError as e:
            logging.error(f"Error setting user: {e}")
            await session.rollback()
            return None


async def add_user(tg_id) -> bool:
    """
    Регистрация нового пользователя бота (заносим его телеграм ID)
    :param tg_id:
    :return: True если пользователь был добавлен, False если он уже существует
    """
    async with session_manager() as session:
        try:
            session.add(User(telegram_id=tg_id))
            await session.commit()
            return True
        except SQLAlchemyError as e:
            logging.error(f"Error setting user: {e}")
            await session.rollback()
            return False


async def add_new_user_profile(
    tg_id: int,
    full_name: str = None,
    email: str = None,
    phone_number: str = None,
    city: str = None,
    status_in_germany: str = None,
) -> bool:
    """
    Добавляем новый профиль пользователя в БД
    :param tg_id:
    :param full_name:
    :param email:
    :param phone_number:
    :param city:
    :param status_in_germany:
    :return: True если профиль был добавлен, False если произошла ошибка
    """
    async with session_manager() as session:
        try:
            user = await session.scalar(select(User).where(User.telegram_id == tg_id))
            if not user:
                user = User(telegram_id=tg_id)
                session.add(user)
                await session.commit()  # commit first to get the id
                user = await session.scalar(select(User).where(User.telegram_id == tg_id))  # повторный запрос для получения id

            user_profile = UserProfile(
                user_id=user.id,
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                city=city,
                status_in_germany=status_in_germany,
            )
            session.add(user_profile)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            logging.error(f"Error adding user profile: {e}")
            await session.rollback()
            return False


# Асинхронная функция для загрузки вопросов из БД
async def load_questions():
    """Загрузка всех вопросов из БД с вариантами ответов"""
    async with session_manager() as session:
            try:
                questions_result = await session.execute(select(Question))
                questions = questions_result.scalars().all()

                all_questions = []
                for question in questions:
                        options_result = await session.execute(
                            select(AnswerOption).where(AnswerOption.question_id == question.id)
                        )
                        options = options_result.scalars().all()
                        all_questions.append({
                            "question": question.question_text,
                            "options": [option.option_text for option in options],
                            "type": question.type,
                        })
                return all_questions
            except SQLAlchemyError as e:
                logging.error(f"Error load questions: {e}")
                await session.rollback()
                return []


async def add_questions_with_options(questions_data: List[Dict[str, Any]]) -> None:
    """Добавляет вопросы и варианты ответов в базу данных."""
    async with session_manager() as session:
        try:
            for question_data in questions_data:
                question_text = question_data["question"]
                question_type = question_data.get("type", "single_choice")  # Default to single_choice if not provided

                question = Question(question_text=question_text, type=question_type)
                session.add(question)
                await session.flush()  # Flush to get id for the question

                for option_data in question_data["options"]:
                    option_text = option_data["text"]
                    score = option_data.get("score", 0)  # Default to 0 if not provided
                    option = AnswerOption(question_id=question.id, option_text=option_text, score=score)
                    session.add(option)

                await session.commit()
                logging.info(f"Question '{question_text}' and its options added successfully.")

        except SQLAlchemyError as e:
            logging.error(f"Error adding question and options: {e}")
            await session.rollback()


async def is_tables_empty() -> bool:
    """Проверяет, пусты ли таблицы questions и answer_options."""
    async with session_manager() as session:
        try:
            questions_result = await session.execute(select(Question))
            questions = questions_result.scalars().all()

            options_result = await session.execute(select(AnswerOption))
            options = options_result.scalars().all()

            return not bool(questions) and not bool(options)  # True if BOTH are empty
        except SQLAlchemyError as e:
            logging.error(f"Error checking if tables are empty: {e}")
            return True  # treat as empty to add questions in case of error


async def add_question_data():
    """Добавляет тестовые данные в БД"""
    if await is_tables_empty():
        questions_data = [
            {
                "question": "Ваши цели и планы на ближайшие 5 лет?\n📌 Выберите несколько вариантов ответа.",
                "type": "multiple_choice",
                "options": [
                    {"text": "Покупка жилья"},
                    {"text": "Получение жилищных субсидий"},
                    {"text": "Сбережения для детей"},
                    {"text": "Оптимизация налогов"},
                    {"text": "Пенсионное обеспечение"},
                    {"text": "Сохранение накопленного капитала"},
                    {"text": "Увеличение капитала"},
                    {"text": "Дополнительный доход"},
                ],
            },
            {
                "question": "Ваш возраст?",
                "options": [
                    {"text": "От 18 до 35 лет"},
                    {"text": "От 35 до 45 лет"},
                    {"text": "Старше 45 лет"},
                ],
            },
            {
                "question": "Семейное положение?",
                "options": [
                    {"text": "Холост / не замужем"},
                    {"text": "Женат / замужем"},
                    {"text": "Вдовец / вдова"},
                ],
            },
            {
                "question": "Количество детей до 18 лет?",
                "options": [
                    {"text": "0", "score": 5},
                    {"text": "1", "score": 4},
                    {"text": "2", "score": 3},
                    {"text": "3 и более", "score": 2},
                ],
            },
            {
                "question": "Текущая занятость?",
                "options": [
                    {"text": "Бессрочный договор (unbefristet), госслужащий (Beamter)"},
                    {"text": "Самозанятый или владелец бизнеса"},
                    {"text": "Временный трудовой договор (befristet) или MiniJob"},
                    {"text": "100% поддержка государства (JC - Bürgergeld/Socialamt)"},
                ],
            },
            {
                "question": "Доход на семью после уплаты налогов (нетто) в месяц?",
                "options": [
                    {"text": "Менее 2 500 евро"},
                    {"text": "От 2 500 до 3 499 евро"},
                    {"text": "От 3 500 до 4 499 евро"},
                    {"text": "От 4 500 евро и выше"},
                ],
            },
            {
                "question": "Хочу получать предложения о подработке в финансовой сфере!",
                "options": [
                    {"text": "Да"},
                    {"text": "Нет"},
                ],
            },
            {
                "question": "Уровень владения немецким языком?",
                "options": [
                    {"text": "A1–A2 (начальный уровень)"},
                    {"text": "B1 (средний уровень)"},
                    {"text": "B2 (уверенный уровень)"},
                    {"text": "C1 и выше (свободное владение)"},
                ],
            },
            {
                "question": "Обеспеченность жильем? (Выберите один или несколько вариантов ответа)",
                "type": "multiple_choice",
                "options": [
                    {"text": "Аренда жилья (самостоятельная оплата)"},
                    {"text": "Аренда жилья (поддержка государства)"},
                    {"text": "Собственное жилье с ипотекой"},
                    {"text": "Собственное жилье"},
                    {"text": "Иное (проживание у родственников)"},
                ],
            },
            {
                "question": "Наличие финансовых продуктов? (Выберите один или несколько вариантов ответа)",
                "type": "multiple_choice",
                "options": [
                    {"text": "Riester Rente / Basis Rente / Rürup-Rente"},
                    {"text": "Zukunftsplan für Kinder (Накопления на будущее детей)"},
                    {"text": "Bausparvertrag"},
                    {"text": "Zusatzversicherung Zahn (Доп. стоматологическая страховка)"},
                    {"text": "Berufsunfähigkeitsversicherung (Защита от потери трудоспособности)"},
                    {"text": "Инвестирую в фонды"},
                    {"text": "Пока не воспользовался"},
                ],
            },
        ]
        await add_questions_with_options(questions_data)
    else:
        logging.info("Questions and options are already in the table. Skipping adding.")


async def main():
    # Пример использования:
    registration_data = {
        "tg_id": 123456789,
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "city": "Berlin",
        "status_in_germany": "Verheiratet",  # Пример статуса
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
