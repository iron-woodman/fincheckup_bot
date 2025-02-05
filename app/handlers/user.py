from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date

from app.database.requests2 import add_new_user_profile
from app.utils.validators import (validate_email, validate_age, validate_phone, validate_full_name, validate_city_name,
                                  validate_user_status)


class UserProfileData(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_email = State()
    waiting_for_phone_number = State()
    waiting_for_city = State()
    waiting_for_status_in_germany = State()



user_router = Router()

# Словарь для хранения данных
user_data = {}


@user_router.callback_query(F.data == 'start_test')
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
        await message.answer('Сбор анктных данных завершен')
        data = await state.get_data()
        print(data)
        await message.answer(f'ФИО: {data["full_name"]}\n'
                             f'Ваш e-mail: {data["email"]}\n'
                             f'Телефон: {data["phone_number"]}\n'
                             f'Город: {data["city"]}\n'
                             f'Статус: {data["status_in_germany"]}\n'
                             )
        await message.answer('Сохранение данных в БД...')

    else:
        await message.answer("Пожалуйста, укажите корректный статус в Германии.")



#
#
# @user_router.message(UserProfileData.waiting_for_age)
# async def register_age(message: Message, state: FSMContext):
#     try:
#         if validate_age(message.text):
#             await state.update_data(age=int(message.text))
#             await state.set_state(UserProfileData.waiting_for_email)
#             await message.answer('Ваш e-mail:')
#         else:
#             await message.answer("Пожалуйста, введите корректный возраст (положительное число).")
#     except ValueError:
#         await message.answer("Пожалуйста, введите корректный возраст.")





# @user_router.message(UserProfileData.waiting_for_phone)
# async def register_email(message: Message, state: FSMContext):
#     phone = message.text
#     if validate_phone(phone):
#         await state.update_data(phone=phone)
#         await state.set_state(UserProfileData.waiting_for_child_count)
#         await message.answer('Количество детей до 18 лет:')
#     else:
#         await message.answer("Пожалуйста, введите корректный номер телефона.")

#
# @user_router.message(UserProfileData.waiting_for_child_count)
# async def register_child_count(message: Message, state: FSMContext):
#     try:
#         child_count = int(message.text)
#         if child_count >= 0:
#             await state.update_data(child_count=child_count)
#             data = await state.get_data()
#             print(data)
#             await message.answer(f'Ваше имя: {data["name"]}\n'
#                                  f'Ваш возраст: {data["age"]}\n'
#                                  f'Количество детей: {data["child_count"]}\n'
#                                  f'Ваш e-mail: {data["email"]}\n'
#                                  f'Телефон: {data["phone"]}\n')
#             await message.answer('Сохранение данных в БД...')
#
#             tg_id = message.from_user.id
#             registration_data = {
#                 "tg_id": tg_id,
#                 "first_name": data["name"],
#                 "last_name": "Doe",
#                 "birth_date": date(1990, 5, 15),
#                 "marriage_status": MarriageStatus.VERHEIRATET,
#                 "phone_number": data["phone"],
#                 "email": data["email"],
#                 "children_under_18": data["child_count"]
#             }
#
#             success = await add_new_user_profile(**registration_data)
#             if success:
#                 print("User profile added successfully.")
#             else:
#                 print("Failed to add user profile.")
#             await state.clear()  # Завершаем диалог
#         else:
#             await message.answer("Пожалуйста, введите неотрицательное количество детей.")
#     except ValueError:
#         await message.answer("Пожалуйста, введите корректное число детей.")
