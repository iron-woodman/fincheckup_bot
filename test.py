import json
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (Message, CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup)
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Замените на токен вашего бота
BOT_TOKEN = "7541180377:AAHcSumNNnfYmp4FQKRFA8wf3hcRF5UOfhY"

# Загрузка вопросов из JSON файла
def load_questions(filename="questions.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# Создание inline-клавиатуры для вариантов ответа
def create_keyboard(options, prefix):
    builder = InlineKeyboardBuilder()
    for index, option in enumerate(options):
       builder.add(InlineKeyboardButton(text=option, callback_data=f"{prefix}_{index}"))
    return builder.adjust(2).as_markup()

# Глобальный словарь для хранения ответов пользователя и текущего вопроса
user_states = {}


# Создание Router
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user_id = message.from_user.id
    user_states[user_id] = {"answers": [], "question_index": 0}
    questions = load_questions()
    if not questions:
        await message.answer("Нет вопросов для опроса")
        return

    question_data = questions[0]
    question_text = question_data["question"]
    keyboard = create_keyboard(question_data["options"], prefix="option")
    await message.answer(question_text, reply_markup=keyboard)



@router.callback_query(F.data.startswith("option_"))
async def handle_answer(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if user_id not in user_states:
         await callback.answer("Сначала нажмите /start")
         return
    user_state = user_states[user_id]
    questions = load_questions()
    question_index = user_state["question_index"]
    if question_index >= len(questions):
         await callback.answer("Опрос завершен")
         return
    selected_option_index = int(callback.data.split("_")[1])
    selected_option = questions[question_index]["options"][selected_option_index]
    user_state["answers"].append(selected_option)

    user_state["question_index"] += 1
    question_index = user_state["question_index"]


    if question_index < len(questions):
        question_data = questions[question_index]
        question_text = question_data["question"]
        keyboard = create_keyboard(question_data["options"], prefix="option")
        await callback.message.edit_text(text=question_text, reply_markup=keyboard)
        await callback.answer()
    else:
        answers = user_state["answers"]
        result_text = "Ваши ответы:\n" + "\n".join([f"{index + 1}. {answer}" for index, answer in enumerate(answers)])
        await callback.message.edit_text(result_text)
        del user_states[user_id]


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
