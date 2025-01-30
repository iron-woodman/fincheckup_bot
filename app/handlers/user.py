from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date

from app.database.requests2 import add_new_user_profile
from app.database.models2 import MarriageStatus
from app.utils.validators import validate_email, validate_age, validate_phone


class UserData(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_child_count = State()


user_router = Router()

# Словарь для хранения данных
user_data = {}


@user_router.callback_query(F.data == 'start_test')
async def register(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserData.waiting_for_name)
    await callback.message.answer('Введите ваше имя:')


@user_router.message(UserData.waiting_for_name)
async def register_name(message: Message, state: FSMContext):
    if message.text:  # Проверка на непустое имя
        await state.update_data(name=message.text)
        await state.set_state(UserData.waiting_for_age)
        await message.answer('Сколько вам лет:')
    else:
        await message.answer("Пожалуйста, введите ваше имя.")


@user_router.message(UserData.waiting_for_age)
async def register_age(message: Message, state: FSMContext):
    try:
        if validate_age(message.text):
            await state.update_data(age=int(message.text))
            await state.set_state(UserData.waiting_for_email)
            await message.answer('Ваш e-mail:')
        else:
            await message.answer("Пожалуйста, введите корректный возраст (положительное число).")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст.")


@user_router.message(UserData.waiting_for_email)
async def register_email(message: Message, state: FSMContext):
    email = message.text
    if validate_email(email):
        await state.update_data(email=email)
        await state.set_state(UserData.waiting_for_phone)
        await message.answer('Контактный телефон:')
        # await message.answer('Контактный телефон:', reply_markup=phone_kb)  # Оставляю на случай, если нужна клавиатура
    else:
        await message.answer("Пожалуйста, введите корректный e-mail.")


@user_router.message(UserData.waiting_for_phone)
async def register_email(message: Message, state: FSMContext):
    phone = message.text
    if validate_phone(phone):
        await state.update_data(phone=phone)
        await state.set_state(UserData.waiting_for_child_count)
        await message.answer('Количество детей до 18 лет:')
    else:
        await message.answer("Пожалуйста, введите корректный номер телефона.")


@user_router.message(UserData.waiting_for_child_count)
async def register_child_count(message: Message, state: FSMContext):
    try:
        child_count = int(message.text)
        if child_count >= 0:
            await state.update_data(child_count=child_count)
            data = await state.get_data()
            print(data)
            await message.answer(f'Ваше имя: {data["name"]}\n'
                                 f'Ваш возраст: {data["age"]}\n'
                                 f'Количество детей: {data["child_count"]}\n'
                                 f'Ваш e-mail: {data["email"]}\n'
                                 f'Телефон: {data["phone"]}\n')
            await message.answer('Сохранение данных в БД...')

            tg_id = message.from_user.id
            registration_data = {
                "tg_id": tg_id,
                "first_name": data["name"],
                "last_name": "Doe",
                "birth_date": date(1990, 5, 15),
                "marriage_status": MarriageStatus.VERHEIRATET,
                "phone_number": data["phone"],
                "email": data["email"],
                "children_under_18": data["child_count"]
            }

            success = await add_new_user_profile(**registration_data)
            if success:
                print("User profile added successfully.")
            else:
                print("Failed to add user profile.")
            await state.clear()  # Завершаем диалог
        else:
            await message.answer("Пожалуйста, введите неотрицательное количество детей.")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число детей.")
