from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
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


catalog =InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Кроссовки', callback_data='boots')],
    [InlineKeyboardButton(text='Футболки', callback_data='t-shirt')],
    [InlineKeyboardButton(text='Кепки', callback_data='caps')]
])


get_phone_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить номер',
                                                                       request_contact=True)]],
                                       resize_keyboard=True)

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

