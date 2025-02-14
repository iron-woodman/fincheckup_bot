import asyncio

from datetime import date
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from app.database.database import get_async_session
from app.database.models import User, UserProfile, Question, AnswerOption, QuestionType, UserAnswerOptions

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
    Добавляем или обновляем профиль пользователя в БД. Если профиль существует, он будет обновлен.
    :param tg_id:
    :param full_name:
    :param email:
    :param phone_number:
    :param city:
    :param status_in_germany:
    :return: True, если профиль был добавлен или обновлен, False в случае ошибки.
    """
    async with session_manager() as session:
        try:
            user = await session.scalar(select(User).where(User.telegram_id == tg_id))

            if not user:
                user = User(telegram_id=tg_id)
                session.add(user)
                await session.flush()  # Flush to get the user.id
                user = await session.scalar(select(User).where(User.telegram_id == tg_id)) #Re-fetch user to ensure it's in the session
                if not user:
                    logging.error(f"Failed to retrieve user after creation.")
                    await session.rollback()
                    return False

            # Проверяем наличие существующего профиля
            existing_profile = await session.scalar(select(UserProfile).where(UserProfile.user_id == user.id))

            if existing_profile:
                # Обновляем существующий профиль
                existing_profile.full_name = full_name
                existing_profile.email = email
                existing_profile.phone_number = phone_number
                existing_profile.city = city
                existing_profile.status_in_germany = status_in_germany
            else:
                # Создаем новый профиль
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
            logging.error(f"Error adding/updating user profile: {e}")
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
                            "id": question.id,  # Добавлено
                            "question": question.question_text,
                            "options": [option.option_text for option in options],
                            "type": question.type,
                        })
                return all_questions
            except SQLAlchemyError as e:
                logging.error(f"Error load questions: {e}")
                await session.rollback()
                return []



async def save_answer(user_id: int, question_id: int, selected_options: List[str]):
    """Сохраняет ответы пользователя в базу данных."""
    async with session_manager() as session:
        try:
            # Get the question
            question = await session.execute(
                select(Question).options(selectinload(Question.options)).where(Question.id == question_id)
            )
            question = question.scalar()

            if question:
                for i in selected_options:
                    try:
                        option_index = int(i)
                        option = question.options[option_index]

                        # Create a new UserAnswerOptions record
                        user_answer_option = UserAnswerOptions(
                            user_id=user_id,
                            question_id=question_id,
                            answer_option_id=option.id
                        )
                        session.add(user_answer_option)

                        logging.info(f"Saved UserAnswerOptions for user {user_id}, question {question_id}, option {option.id}")
                    except (IndexError, ValueError) as e:
                        logging.error(f"Invalid option index: {i}. Error: {e}")
                        await session.rollback()
                        return  # Exit if an invalid option is found

            await session.commit()
            logging.info(f"Answers saved successfully for user {user_id}, question {question_id}")
        except Exception as e:
            logging.error(f"Error saving answers: {e}")
            await session.rollback()



async def add_questions_with_options(questions_data: List[Dict[str, Any]]) -> None:
    """Добавляет вопросы и варианты ответов в базу данных."""
    async with session_manager() as session:
        try:
            for q_data in questions_data:
                question_text = q_data["question"]
                question_type = q_data.get("question_type", "single_choice")  # Default to single_choice if not provided. Use "type" instead of "question_type"
                question_type = QuestionType(question_type)
                question = Question(question_text=question_text, type=question_type)
                session.add(question)
                await session.flush()  # Flush to get id for the question

                for option_data in q_data["options"]:
                    option = AnswerOption(question_id=question.id, option_text=option_data)
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


async def clear_questions_and_options() -> None:
    """Очищает таблицы questions и answer_options."""
    async with session_manager() as session:
        try:
            # Сначала удаляем все записи из answer_options
            await session.execute(delete(AnswerOption))

            # Затем удаляем все записи из questions
            await session.execute(delete(Question))

            # Подтверждаем изменения
            await session.commit()
            logging.info("Tables questions and answer_options cleared successfully.")
        except SQLAlchemyError as e:
            logging.error(f"Error clearing tables: {e}")
            await session.rollback()

    # Пример использования:
    # await clear_questions_and_options()

async def get_user_answers(telegram_id: int) -> List[str]:
    """
    Получает все ответы пользователя из базы данных на основе telegram_id.

    Args:
        telegram_id: Telegram ID пользователя.

    Returns:
        Список выбранных ответов пользователя.
        Если ответов нет, возвращает пустой список.
    """
    async with session_manager() as session:
        try:
            # Находим пользователя по telegram_id
            user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

            if not user:
                return []  # Пользователь не найден, возвращаем пустой список

            # Получаем все ответы пользователя
            answers = await session.scalars(select(UserAnswerOptions).where(UserAnswerOptions.user_id == user.id))
            answers = answers.all()

            # Преобразуем результаты в список словарей для удобства использования
            result = []
            for answer in answers:
                # Получаем текст варианта ответа
                answer_option = await session.scalar(select(AnswerOption).where(AnswerOption.id == answer.answer_option_id))
                answer_text = answer_option.option_text if answer_option else None
                result.append(answer_text)

            return result
        except SQLAlchemyError as e:
            logging.error(f"Error getting user answers: {e}")
            await session.rollback()
            return []


async def get_user_answers_total_info(telegram_id: int) -> List[Dict[str, Any]]:
    """
    Получает все ответы пользователя из базы данных на основе telegram_id.

    Args:
        telegram_id: Telegram ID пользователя.

    Returns:
        Список словарей, где каждый словарь представляет собой ответ пользователя.
        Если ответов нет, возвращает пустой список.
    """
    async with session_manager() as session:
        try:
            # Находим пользователя по telegram_id
            user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

            if not user:
                return []  # Пользователь не найден, возвращаем пустой список

            # Получаем все ответы пользователя
            answers = await session.scalars(select(UserAnswerOptions).where(UserAnswerOptions.user_id == user.id))
            answers = answers.all()

            # Преобразуем результаты в список словарей для удобства использования
            result = []
            for answer in answers:
                # Получаем текст варианта ответа
                answer_option = await session.scalar(select(AnswerOption).where(AnswerOption.id == answer.answer_option_id))
                answer_text = answer_option.option_text if answer_option else None

                # Получаем текст вопроса
                question = await session.scalar(select(Question).where(Question.id == answer.question_id))
                question_text = question.question_text if question else None

                result.append({
                    'id': answer.id,
                    'user_id': answer.user_id,
                    'question_id': answer.question_id,
                    'question_text': question_text, # Added question text
                    'answer_option_id': answer.answer_option_id,
                    'answer_text': answer_text, # Added answer text
                    'created_at': answer.created_at
                })

            return result
        except SQLAlchemyError as e:
            logging.error(f"Error getting user answers: {e}")
            await session.rollback()
            return []


if __name__ == "__main__":
    pass
