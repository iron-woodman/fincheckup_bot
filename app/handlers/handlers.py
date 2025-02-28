## -*- coding: utf-8 -*-

from aiogram import  F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import app.keyboards.user_keyboards as kb
import app.database.requests as rq


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    new_user = await rq.set_user(message.from_user.id) # регистриуем в БД нового пользователя
    if new_user:
        # новый пользователь
        await message.answer('Здравствуйте! Пройдите небольшое тестирование.', reply_markup=kb.main)
    else:
        # пользователь не новый
        await message.answer('И снова здравствуйте! Пройдите небольшое тестирование.', reply_markup=kb.start_test)



@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Помощь.')



@router.message(F.text == 'Каталог')
async def catalog(message: Message):
    await message.answer('Выберите категорию товара', reply_markup=await kb.categories())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer('Выберите товар по категории',
                                  reply_markup=await kb.items(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('item_'))
async def item(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])
    await callback.answer('Вы выбрали товар')
    await callback.message.answer(f'Название: {item_data.waiting_for_name}'
                                  f'\nОписание: {item_data.description}'
                                  f'\nЦена: {item_data.price} $',
                                  reply_markup=await kb.items(callback.data.split('_')[1]))

@router.callback_query(F.data == 'to_main')
async def main_menu(callback: CallbackQuery):
    await callback.answer('Вернулись в главное меню')
    await callback.answer('', reply_markup=kb.main)



