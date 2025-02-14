import logging
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date
from app.config import MANAGER_TELEGRAM_ID
from app.database.requests2 import add_new_user_profile, get_user_answers
from app.utils.matrix import Matrix
from app.utils.shablon import Shablon
from app.keyboards.user_keyboards import consult_record
from app.utils.validators import (validate_email, validate_age, validate_phone, validate_full_name, validate_city_name,
                                  validate_user_status)


class UserProfileData(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_email = State()
    waiting_for_phone_number = State()
    waiting_for_city = State()
    waiting_for_status_in_germany = State()


logging.basicConfig(level=logging.INFO)

user_router = Router()

# Словарь для хранения данных
user_data = {}

# @user_router.callback_query(F.data == 'start_test')
# @user_router.callback_query(F.data == 'start_user_profile')
# @user_router.message(F.data == 'Тест завершен!')
@user_router.callback_query(F.data == 'user_profile')
async def register(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserProfileData.waiting_for_full_name)
    await callback.message.answer('Введите ваши ФИО:')


@user_router.message(UserProfileData.waiting_for_full_name)
async def register_full_name(message: Message, state: FSMContext):
    full_name = message.text
    if validate_full_name(full_name):
        await state.update_data(full_name=full_name)
        await state.set_state(UserProfileData.waiting_for_email)
        await message.answer('Ваш email:')
    else:
        await message.answer("Пожалуйста, введите корректные ФИО.")


@user_router.message(UserProfileData.waiting_for_email)
async def register_email(message: Message, state: FSMContext):
    email = message.text
    if validate_email(email):
        await state.update_data(email=email)
        await state.set_state(UserProfileData.waiting_for_phone_number)
        await message.answer('Контактный телефон:')
    else:
        await message.answer("Пожалуйста, введите корректный e-mail.")


@user_router.message(UserProfileData.waiting_for_phone_number)
async def register_phone_number(message: Message, state: FSMContext):
    phone = message.text
    if validate_phone(phone):
        await state.update_data(phone_number=phone)
        await state.set_state(UserProfileData.waiting_for_city)
        await message.answer('Город:')
    else:
        await message.answer("Пожалуйста, введите корректный номер телефона.")


@user_router.message(UserProfileData.waiting_for_city)
async def register_phone_number(message: Message, state: FSMContext):
    city = message.text
    if validate_city_name(city):
        await state.update_data(city=city)
        await state.set_state(UserProfileData.waiting_for_status_in_germany)
        await message.answer('Статус в Германии:')
    else:
        await message.answer("Пожалуйста, введите корректное название города.")


@user_router.message(UserProfileData.waiting_for_status_in_germany)
async def register_phone_number(message: Message, state: FSMContext):
    status_in_germany = message.text
    if validate_city_name(status_in_germany):
        await state.update_data(status_in_germany=status_in_germany)
        await state.set_state(UserProfileData.waiting_for_status_in_germany)
        # await message.answer('Сбор анктных данных завершен')
        data = await state.get_data()
        print(data)

        try:
            data['tg_id'] = message.from_user.id
            success = await add_new_user_profile(**data)
            if success:
                print("User profile added successfully.")
                # подсчитываем количество набранных баллов пользователем и выводим ему соответсующее сообщение
                user_answers = await get_user_answers(message.from_user.id)
                matrix = Matrix(r'quiz_data\quiz_matrix.xlsx')
                await matrix.process_matrix_file(matrix.excel_file)  # Загрузка файла
                user_points = await matrix.calculate_points(user_answers)
                print('user_points:', user_points)
                shablon = Shablon(r'quiz_data\quiz_shablon.xlsx')
                await shablon.process_shablon_file()
                await shablon.extract_shablon_data()
                user_results = await shablon.get_shablon(user_points)
                print(user_results)
                # await message.answer(user_results)
                if user_results is None:
                    user_results = "---"
                await message.answer(user_results, reply_markup=consult_record)
            else:
                print("Failed to add user profile.")
        except Exception as e:
            logging.error(f"Ошибка добавления профиля пользователя {e}")

    else:
        await message.answer("Пожалуйста, укажите корректный статус в Германии.")


@user_router.callback_query(F.data == 'consult_record')
async def record_for_consult(callback: CallbackQuery, state: FSMContext, bot: Bot):
    # Получаем данные из FSMContext (если они еще там есть)
    try:
        data = await state.get_data()
    except Exception as e:
        logging.error(f"Не удалось получить данные из state: {e}")
        data = {} # Если данных нет, создаем пустой словарь

    # Формируем сообщение для менеджера
    user_info = f"Новая запись на консультацию:\n" \
                f"ФИО: {data.get('full_name', 'Не указано')}\n" \
                f"Email: {data.get('email', 'Не указано')}\n" \
                f"Телефон: {data.get('phone_number', 'Не указано')}\n" \
                f"Город: {data.get('city', 'Не указано')}\n" \
                f"Статус: {data.get('status_in_germany', 'Не указано')}\n" \
                f"Telegram ID: {callback.from_user.id}\n" \
                f"Telegram Username: @{callback.from_user.username if callback.from_user.username else 'Не указано'}"

    # Отправляем сообщение менеджеру
    try:
        await bot.send_message(chat_id=MANAGER_TELEGRAM_ID, text=user_info)
        logging.info(f"Данные пользователя отправлены менеджеру {MANAGER_TELEGRAM_ID}")
    except Exception as e:
        logging.error(f"Ошибка при отправке данных менеджеру: {e}")

    await callback.message.answer('Вы записались на консультацию!')
