## -*- coding: utf-8 -*-

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any

# from app.database.requests import get_categories, get_category_item



main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Каталог')],
    [KeyboardButton(text='Корзина')],
    [KeyboardButton(text='Контакты'),
    KeyboardButton(text='О нас')]
                                     ],
input_field_placeholder='Выберите вариант ответа:',
resize_keyboard=True)



start_test =InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать опрос', callback_data='start_test')]
    # [InlineKeyboardButton(text='Начать опрос')]
])


personal_data =InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтверждаю', callback_data='user_profile')]
])

consult_record =InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Записаться на встречу', callback_data='consult_record')]
])


catalog =InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Кроссовки', callback_data='boots')],
    [InlineKeyboardButton(text='Футболки', callback_data='t-shirt')],
    [InlineKeyboardButton(text='Кепки', callback_data='caps')]
])


get_phone_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить номер',
                                                                       request_contact=True)]],
                                       resize_keyboard=True)


# опции обработки персональных данных
allow_personal_data_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, соглашаюсь", callback_data="allow_personal_data:yes")],
    [InlineKeyboardButton(text="❌ Нет, напомнить позже", callback_data="allow_personal_data:no")],
])

# ---------------------- статус в германии ---------------------------------------------

user_status_in_germany_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Гражданство Германии", callback_data="Гражданство Германии")],
    [InlineKeyboardButton(text="ПМЖ", callback_data="ПМЖ")],
    [InlineKeyboardButton(text="ВНЖ", callback_data="ВНЖ")],
    [InlineKeyboardButton(text="Голубая карта ЕС", callback_data="Голубая карта ЕС")],
    [InlineKeyboardButton(text="Другое", callback_data="Другое")],
])

# --------------------------------------------------------------------------------------

# Функция для создания Inline-клавиатуры
def create_keyboard(options: List[str], is_multiple_choice: bool = False, selected_options: set = None):
    keyboard = []
    if selected_options is None:
        selected_options = set()
    for i, option in enumerate(options):
        key = str(i)  # Using index as key
        text = f"{'✅ ' if key in selected_options else ''}{option}" if is_multiple_choice else option
        callback_data = f"option_{key}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    if is_multiple_choice:
        keyboard.append([InlineKeyboardButton(text="Готово", callback_data="done")])  # Кнопка "Готово"
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# async def categories():
#     all_categories = await get_categories()
#     keyboard = InlineKeyboardBuilder()
#     for category in all_categories:
#         # keyboard.add(InlineKeyboardButton(text=category.waiting_for_name))
#         print('Категория:', category.id, category.waiting_for_name)
#         keyboard.add(InlineKeyboardButton(text=category.waiting_for_name, callback_data=f"category_{category.id}"))
#     keyboard.add(InlineKeyboardButton(text='На главную...', callback_data='to_main'))
#     return keyboard.adjust(2).as_markup()# в одном ряду до 2-х кнопок


# async def items(category_id):
#     print('async def items(category_id):')
#     all_items = await get_category_item(category_id)
#     keyboard = InlineKeyboardBuilder()
#     for item in all_items:
#         print('модель:', item.waiting_for_name)
#         keyboard.add(InlineKeyboardButton(text=item.waiting_for_name, callback_data=f"item_{item.id}"))
#     keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
#     return keyboard.adjust(2).as_markup()# в одном ряду до 2-х кнопок

