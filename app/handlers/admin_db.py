import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram import F, Router, types, Bot
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.enums import ParseMode

from app.database.models import User, UserProfile, Question, AnswerOption, UserAnswerOptions
from app.database.requests import clean_tables, TABLES_TO_CLEAN

db_router = Router()



# Состояние выбора таблиц
selected_tables = set()

def get_tables_keyboard():
    """Создает инлайн-клавиатуру со списком таблиц."""
    keyboard = []
    for table_name in TABLES_TO_CLEAN:
        # Добавляем галочку, если таблица уже выбрана
        text = f"{table_name} {'✅' if table_name in selected_tables else ''}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"table:{table_name}")])

    keyboard.append([InlineKeyboardButton(text="Очистить выбранные таблицы", callback_data="clear_tables")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@db_router.callback_query(lambda c: c.data.startswith("table:"))
async def table_selection(callback: CallbackQuery):
    """Обработчик нажатий на кнопки выбора таблиц."""
    table_name = callback.data.split(":")[1]

    if table_name in selected_tables:
        selected_tables.remove(table_name)
    else:
        selected_tables.add(table_name)

    keyboard = get_tables_keyboard()
    await callback.message.edit_text(
        text="Выбери таблицы для очистки:", reply_markup=keyboard
    )
    await callback.answer()


@db_router.callback_query(lambda c: c.data == "clear_tables")
async def clear_tables(callback: CallbackQuery):
    """Обработчик нажатия на кнопку "Очистить выбранные таблицы"."""
    if not selected_tables:
        await callback.message.edit_text("Не выбрано ни одной таблицы для очистки.")
        await callback.answer()
        return

        # Запрашиваем подтверждение
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, очистить", callback_data="confirm_clear")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_clear")],
    ])
    await callback.message.edit_text(
        text=f"Вы уверены, что хотите очистить таблицы: {', '.join(selected_tables)}?",
        reply_markup=keyboard,
    )
    await callback.answer()

@db_router.callback_query(lambda c: c.data == "confirm_clear")
async def confirm_clear(callback: CallbackQuery):
    """Обработчик подтверждения очистки таблиц."""
    try:
        await clean_tables(selected_tables)
        await callback.message.edit_text(
            f"Таблицы {', '.join(selected_tables)} успешно очищены."
        )
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при очистке таблиц: {e}")
    finally:
        # Сбрасываем состояние выбора таблиц
        selected_tables.clear()
        await callback.answer()


@db_router.callback_query(lambda c: c.data == "cancel_clear")
async def cancel_clear(callback: CallbackQuery):
    """Обработчик отмены очистки таблиц."""
    selected_tables.clear()
    keyboard = get_tables_keyboard()
    await callback.message.edit_text("Очистка таблиц отменена.", reply_markup=keyboard)
    await callback.answer()


@db_router.message(F.text == "База данных")
async def handle_database(message: types.Message):
    keyboard = get_tables_keyboard()
    await message.answer("Выбери таблицы для очистки:",
        reply_markup=keyboard,
    )