import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage


# Токен вашего бота
TOKEN = "7541180377:AAHcSumNNnfYmp4FQKRFA8wf3hcRF5UOfhY"

# Варианты ответа
OPTIONS = {
    'a': "Покупка жилья",
    'b': "Получение жилищных субсидий",
    'c': "Сбережения для детей",
    'd': "Оптимизация налогов",
    'e': "Пенсионное обеспечение",
    'f': "Сохранение накопленного капитала",
    'g': "Увеличение капитала",
    'h': "Дополнительный доход",
}


# Состояние
class UserState(StatesGroup):
    waiting_for_options = State()


# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

logging.basicConfig(level=logging.INFO)


# Функция для создания Inline-клавиатуры
def create_keyboard(selected_options):
    keyboard = []
    for key, value in OPTIONS.items():
        text = f"{'✅ ' if key in selected_options else ''}{value}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"option_{key}")])
    keyboard.append([InlineKeyboardButton(text="Готово", callback_data="done")])  # Кнопка "Готово"
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_options)
    await state.update_data(selected_options=set())  # Инициализация набора выбранных вариантов
    await message.answer(
        "1. Ваши цели и планы на ближайшие 5 лет?\n📌 Выберите несколько вариантов ответа.",
        reply_markup=create_keyboard(set()),
    )


# Обработчик Callback-запросов
@dp.callback_query(UserState.waiting_for_options)
async def button(query: CallbackQuery, state: FSMContext):
    await query.answer()

    data = await state.get_data()
    selected_options = data.get("selected_options", set())

    if query.data.startswith("option_"):
        key = query.data.split("_")[1]
        if key in selected_options:
            selected_options.remove(key)  # Убрать из выбранных
        else:
            selected_options.add(key)  # Добавить в выбранные
    elif query.data == "done":
        # Обработка завершения выбора
        if not selected_options:
            await query.message.edit_text("Вы не выбрали ни одного варианта. Пожалуйста, выберите хотя бы один.")
            return
        selected_options_names = [OPTIONS[key] for key in selected_options]
        await query.message.edit_text(f"Вы выбрали: \n{',\n '.join(selected_options_names)}")
        # Здесь можно сделать дополнительные действия, например, сохранить выбор пользователя
        await state.clear()
        return

    await state.update_data(selected_options=selected_options)
    # Обновление клавиатуры
    await query.message.edit_reply_markup(reply_markup=create_keyboard(selected_options))


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
