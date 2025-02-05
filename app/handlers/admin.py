import aiohttp
from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import os
import pandas as pd
from io import BytesIO
import asyncio


from app.handlers.common import is_admin
from app.keyboards import admin_keyboards
from app.utils.matrix import Matrix

admin_router = Router()


# @admin_router.message(Command('help'))
# async def cmd_help(message: Message):
#     await message.answer('Помощь.')



class UploadingExcelFile(StatesGroup):
    """
    Состояния загрузки файла.
    """
    uploading_matrix = State()
    uploading_shablon = State()


async def save_questions_to_database(df: pd.DataFrame) -> None:
    """
    Сохраняет вопросы из DataFrame в базу данных.
    """

    matrix = Matrix(r'quiz_data\quiz_matrix.xlsx')

    await matrix.process_matrix_file(matrix.excel_file)  # Загрузка файла
    await matrix.extract_questions()
    print('ВОПРОСЫ:', matrix.questions)

    # session = Session()  # Создаем сессию для работы с базой данных
    # try:
    #     for index, row in df.iterrows():  # Проходим по каждой строке DataFrame
    #         quiz_data = QuizData(
    #             column_name1=row['Column1'],  # Замените на ваши названия колонок
    #             column_name2=row['Column2'],  # Замените на ваши названия колонок
    #             # Добавьте другие колонки по мере необходимости
    #         )
    #         session.add(quiz_data)  # Добавляем объект в сессию
    #     session.commit()  # Сохраняем изменения в базе данных
    # except Exception as e:
    #     session.rollback()  # Откат изменений в случае ошибки
    #     print(f"Ошибка при сохранении данных: {e}")
    # finally:
    #     session.close()  # Закрываем сессию



async def process_excel_file(message: types.Message, state: FSMContext, file_type: str) -> None:
    """
    Функция для обработки Excel-файла с матрицей вопросов.
    """
    try:
        async with asyncio.timeout(60):
            await message.answer("Начинаю скачивание файла...")
            file_id = message.document.file_id
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.answer("Файл скачивается...")

            # Загрузка файла через HTTP-запрос
            file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status != 200:
                        await message.answer("Ошибка при загрузке файла.")
                        return
                    file_bytes = await response.read()

            await message.answer("Файл скачан, начинаю чтение...")
            excel_file = BytesIO(file_bytes)
            df = pd.read_excel(excel_file)

            await state.update_data(excel_data=df)

            await message.answer("Файл прочитан, начинаю создание каталога...")
            quiz_data_dir = "quiz_data"
            os.makedirs(quiz_data_dir, exist_ok=True)

            await message.answer("Каталог создан, начинаю сохранение файла...")
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            # file_name = f"quiz_matrix_{timestamp}.xlsx"
            file_name = f"quiz_{file_type}.xlsx"
            full_file_path = os.path.join(quiz_data_dir, file_name)

            with open(full_file_path, 'wb') as f:
                f.write(file_bytes)

            await message.answer("Файл сохранен.")

            num_rows, num_cols = df.shape
            await message.answer(f"Файл успешно загружен, обработан и сохранен в {full_file_path}!\n"
                                 f"Количество строк: {num_rows}\n"
                                 f"Количество столбцов: {num_cols}")

            # Сохранение данных в базу данных
            if file_type == "matrix":
                await save_questions_to_database(df)



    except asyncio.TimeoutError:
        await message.answer("Превышено время ожидания загрузки файла.")

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке файла: {e}")


async def handle_matrix_upload(message: types.Message, state: FSMContext):
    """
    Функция обрабатывающая команду загрузки матрицы
    """
    await message.answer("Загрузите excel-файл с матрицей вопросов:")
    await state.set_state(UploadingExcelFile.uploading_matrix)


async def handle_shablon_upload(message: types.Message, state: FSMContext):
    """
    Функция обрабатывающая команду загрузки матрицы
    """
    await message.answer("Загрузите excel-файл шаблонов ответов:")
    await state.set_state(UploadingExcelFile.uploading_shablon)


@admin_router.message(F.document, UploadingExcelFile.uploading_matrix)
async def process_document(message: types.Message, state: FSMContext):
    if message.document.mime_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return await message.answer("Пожалуйста, загрузите файл в формате Excel (.xlsx)")
    await process_excel_file(message, state, "matrix")
    await state.set_state(state=None)


@admin_router.message(F.document, UploadingExcelFile.uploading_shablon)
async def process_document(message: types.Message, state: FSMContext):
    if message.document.mime_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return await message.answer("Пожалуйста, загрузите файл в формате Excel (.xlsx)")
    await process_excel_file(message, state, "shablon")
    await state.set_state(state=None)


@admin_router.message(F.text == "Загрузить матрицу вопросов")
async def admin_command_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if await is_admin(user_id):
        await handle_matrix_upload(message, state)
    else:
        await message.reply("У вас нет прав для выполнения этой команды.")


@admin_router.message(F.text == "Загрузить шаблоны ответов")
async def handle_answer_templates(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if await is_admin(user_id):
        await handle_shablon_upload(message, state)
    else:
        await message.reply("У вас нет прав для выполнения этой команды.")


@admin_router.message(F.text == "Отчеты")
async def handle_reports(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if await is_admin(user_id):
        await message.answer("Вы выбрали раздел отчетов.\n"
                             "Функционал находится в разработке.")
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")


@admin_router.message(F.text == "База данных")
async def handle_database(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if await is_admin(user_id):
        await message.answer("Вы выбрали раздел базы данных.\n"
                             "Функционал находится в разработке.")
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")

