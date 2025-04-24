## -*- coding: utf-8 -*-

import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload, joinedload
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from app.database.database import get_async_session, async_session_maker
from app.database.models import User, UserProfile, Question, AnswerOption, QuestionType, UserAnswerOptions, UserScore
from app.utils.encripter import encrypt_message, decrypt_message
from app.config import ENCRIPTION_KEY

logging.basicConfig(level=logging.INFO)

# Список таблиц для очистки (должен совпадать с именами классов моделей)
TABLES_TO_CLEAN = {
    "users": User,
    "user_profiles": UserProfile,
    "questions": Question,
    "answer_options": AnswerOption,
    "user_answer_options": UserAnswerOptions,
}


@asynccontextmanager
async def session_manager():
    async for session in get_async_session():
        yield session


# Асинхронный контекстный менеджер для управления сессией
@asynccontextmanager
async def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# async def session_manager():
#     """Asynchronous context manager for SQLAlchemy sessions."""
#     async with get_async_session() as session:  # Используем async with для создания сессии
#         try:
#             yield session
#             await session.commit()
#         except SQLAlchemyError as e:
#             logging.error(f"Session error: {e}")
#             await session.rollback()
#             raise  # Re-raise the exception
#         finally:
#             await session.close()


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


            # шифруем данные пользователя перед занесением в БД
            encrypted_email = await encrypt_message(email, ENCRIPTION_KEY)
            encrypted_phone_number = await encrypt_message(phone_number, ENCRIPTION_KEY)
            encrypted_full_name = await encrypt_message(full_name, ENCRIPTION_KEY)

            if existing_profile:
                # Обновляем существующий профиль
                existing_profile.full_name = encrypted_full_name
                existing_profile.email = encrypted_email
                existing_profile.phone_number = encrypted_phone_number
                existing_profile.city = city
                existing_profile.status_in_germany = status_in_germany
            else:
                # Создаем новый профиль
                user_profile = UserProfile(
                    user_id=user.id,
                    full_name=encrypted_full_name,
                    email=encrypted_email,
                    phone_number=encrypted_phone_number,
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

async def clear_user_answer_options(telegram_id: int) -> None:
    """Очищает таблицу user_answer_options для указанного telegram_id пользователя."""
    async with session_manager() as session:
        try:
            # Find the user based on telegram_id
            user = await session.execute(select(User).where(User.telegram_id == telegram_id)) # Fixed: using select
            user = user.scalar_one_or_none()  # Get the user object or None

            if user:
                # Delete UserAnswerOptions records associated with the user
                deleted_count = await session.execute(
                    delete(UserAnswerOptions).where(UserAnswerOptions.user_id == user.id)  # Use the user's ID
                )
                deleted_count = deleted_count.rowcount #Correcting accessing rowcount
                # Подтверждаем изменения
                await session.commit()
                logging.info(f"Удалено {deleted_count} записей UserAnswerOptions с telegram_id = {telegram_id}")


        except SQLAlchemyError as e:
            logging.error(f"Ошибка при очистке таблицы user_answer_options: {e}")
            await session.rollback()  # Correct the rollback statement


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


async def generate_user_profile_report(start_date: str, end_date: str) -> str | None:
    """Генерирует отчет с данными профилей пользователей за указанный период."""

    try:
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)

        wb = Workbook()
        ws = wb.active
        ws.title = "User Profiles"

        # Заголовки столбцов
        headers = ["User ID", "Telegram ID", "Full Name", "Email", "Phone Number", "City", "Status in Germany",
                   "Registration Date"]
        ws.append(headers)
        # Преобразуем строки в объекты datetime
        start_date = datetime.strptime(start_date, '%d.%m.%Y')
        end_date = datetime.strptime(end_date, '%d.%m.%Y') + timedelta(days=1)  # Включаем последний день

        async with session_manager() as session:
            # Запрос данных из базы данных, явно загружаем профили пользователей
            result = await session.execute(
                select(User)
                .filter(User.created_at >= start_date, User.created_at <= end_date)
                .options(selectinload(User.profile))  # Явно загружаем профиль пользователя
            )
            users = result.scalars().all()

            for user in users:
                # Получаем данные профиля для каждого пользователя
                profile_data = {
                    "User ID": user.id,
                    "Telegram ID": user.telegram_id,
                    "Full Name": await decrypt_message(user.profile.full_name, ENCRIPTION_KEY) if user.profile else "",
                    "Email": await decrypt_message(user.profile.email, ENCRIPTION_KEY) if user.profile else "",
                    "Phone Number": await decrypt_message(user.profile.phone_number, ENCRIPTION_KEY) if user.profile else "",
                    "City": user.profile.city if user.profile else "",
                    "Status in Germany": user.profile.status_in_germany if user.profile else "",
                    "Registration Date": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }

                row = [profile_data[header] for header in headers]
                ws.append(row)

    except SQLAlchemyError as e:
        logging.error(f"Error generating user profile report: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error generating user profile report: {e}")
        return None
    finally:
        filename = f"user_profiles_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"
        filepath = os.path.join(reports_dir, filename)  # Сохраняем в каталоге reports
        # Сохраняем файл
        wb.save(filepath)
        return filepath


async def get_user_answers_data_length(start_date: str, end_date: str) -> str:
    try:
        start_date_dt = datetime.strptime(start_date, '%d.%m.%Y')
        end_date_dt = datetime.strptime(end_date, '%d.%m.%Y') + timedelta(days=1)

        async with session_scope() as session:
            # Проверяем наличие данных в таблице UserAnswerOptions
            count_result = await session.execute(
                select(UserAnswerOptions).filter(
                    UserAnswerOptions.created_at >= start_date_dt,
                    UserAnswerOptions.created_at <= end_date_dt
                )
            )

            # Получаем количество записей
            count = len(count_result.scalars().all())
            return count

    except SQLAlchemyError as e:
        logging.error(f"Error getting user answers data: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None


async def get_user_answers_data(start_date: str, end_date: str) -> str:
    """Получает данные об ответах пользователей и генерирует XLSX-файл."""
    try:
        start_date_dt = datetime.strptime(start_date, '%d.%m.%Y')
        end_date_dt = datetime.strptime(end_date, '%d.%m.%Y') + timedelta(days=1)

        async with session_scope() as session:
            stmt = select(
                    User.telegram_id,
                    Question.question_text,
                    AnswerOption.option_text,
                    UserAnswerOptions.created_at,
                    UserScore.score.label("user_score")
                ).select_from(UserAnswerOptions)  # Указываем начальную таблицу

            stmt = stmt.join(User, UserAnswerOptions.user_id == User.id) # Explicit joins
            stmt = stmt.join(Question, UserAnswerOptions.question_id == Question.id)
            stmt = stmt.join(AnswerOption, UserAnswerOptions.answer_option_id == AnswerOption.id)
            stmt = stmt.outerjoin(UserScore, UserAnswerOptions.user_id == UserScore.user_id)

            stmt = stmt.filter(UserAnswerOptions.created_at >= start_date_dt, UserAnswerOptions.created_at <= end_date_dt)

            result = await session.execute(stmt)

            data = []
            for telegram_id, question_text, option_text, created_at, score in result:
                data.append({
                    "Telegram ID": telegram_id,
                    "Question Text": question_text,
                    "Answer Option Text": option_text,
                    "Answered At": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "Score": score if score is not None else 0
                })

            df = pd.DataFrame(data)

            wb = Workbook()
            ws = wb.active
            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)

            filename = f"user_answers_{start_date_dt.strftime('%Y%m%d')}_{end_date_dt.strftime('%Y%m%d')}.xlsx"
            filepath = f"./reports/{filename}"
            wb.save(filepath)

            return filepath

    except SQLAlchemyError as e:
        logging.error(f"Error getting user answers data: {e}")
        return None
    except Exception as e:
        logging.exception(f"Unexpected error: {e}") # Log the full traceback
        return None



async def clean_tables(selected_tables):
    async for session in get_async_session():
        for table_name in selected_tables:
            table_model = TABLES_TO_CLEAN[table_name]
            # Используем SQLAlchemy для удаления всех записей из таблицы
            await session.execute(delete(table_model))
        await session.commit()


async def upsert_user_score_by_telegram_id(telegram_id: int, score: int) -> bool:
    """Adds or updates a UserScore record based on the user's Telegram ID."""
    async with session_scope() as session:
        try:
            # 1. Get the User object using the Telegram ID
            user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
            if not user:
                logging.warning(f"User with Telegram ID {telegram_id} not found.")
                return False  # User not found

            # 2. Check for existing UserScore record for this user
            existing_score = await session.scalar(select(UserScore).where(UserScore.user_id == user.id))

            if existing_score:
                # Update existing score
                existing_score.score = score
                logging.info(f"Updated score for user (Telegram ID: {telegram_id}), new score: {score}")
            else:
                # Create and add a new score record
                new_score = UserScore(user_id=user.id, score=score)
                session.add(new_score)
                logging.info(f"Added new score for user (Telegram ID: {telegram_id}), score: {score}")

            await session.commit()
            return True

        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemy error upserting user score: {e}", exc_info=True)
            await session.rollback()
            return False
        except Exception as e:
            logging.error(f"Unexpected error upserting user score: {e}", exc_info=True)
            await session.rollback()
            return False


if __name__ == "__main__":
    pass
