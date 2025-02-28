
import logging
from typing import List, Dict, Any

from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.requests import (load_questions, get_user_by_telegram_id, save_answer, clear_user_answer_options)
from app.database.models import QuestionType
from app.keyboards.user_keyboards import create_keyboard, personal_data

# Импортируем session_manager
from app.database.requests import session_manager

# Состояние
class UserState(StatesGroup):
    waiting_for_answer = State()

# Глобальные переменные для хранения вопросов и текущего вопроса
all_questions: List[Dict[str, Any]] = []
current_question_index = 0
logging.basicConfig(level=logging.INFO)

user_test_router = Router()

async def load_data():
    global all_questions
    all_questions = await load_questions()

@user_test_router.callback_query(F.data == 'start_test')
async def start_test(callback: CallbackQuery, state: FSMContext):
    global current_question_index
    current_question_index = 0
    try:
        await load_data()
        print(f"All questions: {all_questions}") # Debug print
        await state.set_state(UserState.waiting_for_answer)

        if not all_questions:
            await callback.message.answer("Вопросы не найдены. Пожалуйста, убедитесь, что база данных заполнена.")
            return

        question = all_questions[current_question_index]
        try:
            await clear_user_answer_options(callback.from_user.id)
        except Exception as e:
            logging.exception(f"Error in clear_user_answer_options({callback.from_user.id}) function: {e}")
            await callback.message.answer(f"Произошла ошибка: {e}")

        try:

            is_multiple_choice = QuestionType(question["type"]) == QuestionType.MULTIPLE_CHOICE
        except ValueError as e:
            logging.error(f"Invalid QuestionType in database: {question['type']}. Error: {e}")
            is_multiple_choice = False

        print("Creating keyboard...")  # Debug print
        keyboard = create_keyboard(question["options"], is_multiple_choice)
        print(f"Keyboard created: {keyboard}") #Debug print

        print("Sending message...") #Debug print
        await callback.message.answer(f"{current_question_index + 1}. {question['question']}", reply_markup=keyboard)
        await state.update_data(question_index=current_question_index, selected_options=set())
    except Exception as e:
        logging.exception(f"Error in start function: {e}")
        await callback.message.answer(f"Произошла ошибка: {e}")

# Обработчик Callback-запросов
@user_test_router.callback_query(UserState.waiting_for_answer)
async def button(query: CallbackQuery, state: FSMContext):
    await query.answer()
    data = await state.get_data()
    question_index = data["question_index"]
    question = all_questions[question_index]
    try:
        is_multiple_choice = QuestionType(question["type"]) == QuestionType.MULTIPLE_CHOICE
    except ValueError:
        # Обработка случая, когда значение в базе данных не является допустимым QuestionType
        logging.error(f"Invalid QuestionType in database: {question['type']}")
        is_multiple_choice = False  # Или другое значение по умолчанию

    selected_options = data.get("selected_options", set())

    if query.data.startswith("option_"):
        key = query.data.split("_")[1]
        if is_multiple_choice:
            if key in selected_options:
                selected_options.remove(key)  # Убрать из выбранных
            else:
                selected_options.add(key)  # Добавить в выбранные
            keyboard = create_keyboard(question["options"], is_multiple_choice, selected_options)
            await query.message.edit_reply_markup(reply_markup=keyboard)  # Update keyboard immediately
            await state.update_data(selected_options=selected_options) # Update selected options
        else:
            # Single choice
            selected_option_index = int(key)
            selected_option_name = question["options"][selected_option_index]

            # Get user and question IDs
            user = await get_user_by_telegram_id(query.from_user.id)
            if user:
                await save_answer(user.id, question["id"], [key])  # save the answer
            else:
                logging.error(f"User not found for telegram_id: {query.from_user.id}")

            await query.message.edit_text(f"Вы выбрали: {selected_option_name}")
            await next_question(query.message, state) # Go to the next question
    elif query.data == "done":
        # Обработка завершения выбора для multiple choice
        if not selected_options:
            # await query.message.edit_text("Вы не выбрали ни одного варианта. Пожалуйста, выберите хотя бы один.")
            await query.answer("Вы не выбрали ни одного варианта. Пожалуйста, выберите хотя бы один.", show_alert=True)
            return  # Exit the handler if no options are selected

        selected_option_names = [question["options"][int(key)] for key in selected_options]

        # Get user and question IDs
        user = await get_user_by_telegram_id(query.from_user.id)
        if user:
            await save_answer(user.id, question["id"], list(selected_options))  # save the answer
        else:
            logging.error(f"User not found for telegram_id: {query.from_user.id}")
        print(selected_option_names)
        await query.message.edit_text(f"Вы выбрали: \n{',\n '.join(selected_option_names)}")
        await next_question(query.message, state)  # Go to the next question

# Функция для перехода к следующему вопросу
async def next_question(message: types.Message, state: FSMContext):
    global current_question_index
    current_question_index += 1

    if current_question_index < len(all_questions):
        question = all_questions[current_question_index]
        try:
            is_multiple_choice = QuestionType(question["type"]) == QuestionType.MULTIPLE_CHOICE
        except ValueError:
            # Обработка случая, когда значение в базе данных не является допустимым QuestionType
            logging.error(f"Invalid QuestionType in database: {question['type']}")
            is_multiple_choice = False  # Или другое значение по умолчанию

        keyboard = create_keyboard(question["options"], is_multiple_choice)
        await message.answer(f"{current_question_index + 1}. {question['question']}", reply_markup=keyboard)
        await state.update_data(question_index=current_question_index, selected_options=set())  # Reset selected_options

        await state.set_state(UserState.waiting_for_answer) # Ensure state is reset
    else:
        await message.answer("Поздравляю, ваши первые результаты готовы!")
        await state.clear()
        await message.answer("Подтвердите согласие на обработку персональных данных.", reply_markup=personal_data)
