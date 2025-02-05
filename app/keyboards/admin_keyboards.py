from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)



# Создаем клавиатуру для администратора
admin_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Загрузить матрицу вопросов")],
    [KeyboardButton(text="Загрузить шаблоны ответов")],
    [KeyboardButton(text="Отчеты"),
    KeyboardButton(text="База данных")]
                                     ],
input_field_placeholder='Ваш выбор:',
resize_keyboard=True)

