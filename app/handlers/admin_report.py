## -*- coding: utf-8 -*-

import logging
from aiogram import F, Router, types, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from app.database.requests import generate_user_profile_report, get_user_answers_data, get_user_answers_data_length

logging.basicConfig(level=logging.INFO)

class ReportForm(StatesGroup):
    date_range = State()
    report_type = State()


report_router = Router()


@report_router.message(F.text == "Отчеты")
async def admin_report(message: types.Message, state: FSMContext):
    """Starts the report generation process."""
    await message.answer("Пожалуйста, введите временной интервал в формате ДД.ММ.ГГГГ-ДД.ММ.ГГГГ:")
    await state.set_state(ReportForm.date_range)


@report_router.message(ReportForm.date_range)
async def get_date_range(message: types.Message, state: FSMContext):
    """Gets the date range from the user."""
    date_range = message.text
    try:
        start_date_str, end_date_str = date_range.split('-')
        start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
        end_date = datetime.strptime(end_date_str, '%d.%m.%Y')

        if start_date > end_date:
            await message.answer("Начальная дата не может быть позже конечной. Пожалуйста, введите временной интервал еще раз.")
            return

    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте ДД.ММ.ГГГГ-ДД.ММ.ГГГГ.")
        return

    await state.update_data(start_date=start_date_str.strip())  # Сохраняем в формате строки, как и раньше
    await state.update_data(end_date=end_date_str.strip())  # Сохраняем в формате строки, как и раньше

    # Создаем инлайн-клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ответы", callback_data="report_type:answers")],
        [InlineKeyboardButton(text="Профили", callback_data="report_type:profile")],
    ])

    await message.answer("Выберите тип отчета:", reply_markup=keyboard)
    await state.set_state(ReportForm.report_type)



@report_router.callback_query(StateFilter(ReportForm.report_type), F.data.startswith("report_type:"))
async def generate_report(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Generates the report based on the provided data."""
    report_type = callback.data.split(":")[1]  # Извлекаем тип отчета из callback_data
    data = await state.get_data()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not start_date or not end_date:
        await callback.message.answer("Необходимо указать временной интервал.")
        await state.clear()
        return

    try:
        if report_type == "profile":
            filepath = await generate_user_profile_report(start_date, end_date)
            # await callback.message.answer("Генерация profile отчетов пока не поддерживается.")
            # await state.clear()
            # return
        elif report_type == "answers":
            # 1. Получаем данные асинхронно
            count = await get_user_answers_data_length(start_date, end_date)
            if count == 0:
                logging.warning(f"За указанный период времени ({start_date} - {end_date}) нет статистики по ответам пользователя.")
                await callback.message.answer("За указанный период времени нет статистики по ответам пользователя.")
                await state.clear()
                return
            else:
                filepath = await get_user_answers_data(start_date, end_date)
        else:
            await callback.message.answer("Неверный тип отчета.")
            await state.clear()
            return

        if filepath:
            try:
                document = FSInputFile(filepath)  # Создаем FSInputFile
                await bot.send_document(callback.message.chat.id, document=document)  # Отправляем документ
            except FileNotFoundError:
                await callback.message.answer("Ошибка: Файл не найден.")
        else:
            await callback.message.answer("Ошибка при генерации отчета. Пожалуйста, проверьте логи.")

    except Exception as e:
        logging.error(f"Error in generate_report handler: {e}")
        await callback.message.answer("Произошла ошибка при генерации отчета.")
    finally:
        await state.clear()  # Clear FSM state
    await callback.answer()  # Обязательно нужно ответить на callbackQuery

