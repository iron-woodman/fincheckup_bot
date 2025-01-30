## -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_TYPE = os.getenv("DB_TYPE", "sqlite") # Выбор СУБД ('mysql' или 'sqlite'). Значение по умолчанию - sqlite
SQLITE_FILE = os.getenv("SQLITE_FILE", "bot.db")
# Получение id админов из .env файла, при отсутствии переменной, вернет пустой список
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",") if admin_id]