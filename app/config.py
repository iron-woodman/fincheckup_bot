## -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
load_dotenv()

KEY_FILE = ".key"  # Имя файла для хранения ключа

def generate_key():
  """Генерирует ключ для AES."""
  return Fernet.generate_key()

def load_key():
  """Загружает ключ из файла, если он существует.  Иначе генерирует, сохраняет и возвращает."""
  if os.path.exists(KEY_FILE):
    try:
      with open(KEY_FILE, "rb") as key_file:
        return key_file.read()
    except Exception as e:
      print(f"Ошибка при чтении ключа из файла: {e}. Будет сгенерирован новый ключ.")
      # Продолжим, как будто файла не было.
      pass # Переходим к генерации нового ключа
  # Если файла нет или произошла ошибка при чтении:
  key = generate_key()
  try:
    with open(KEY_FILE, "wb") as key_file:
      key_file.write(key)
    print(f"Новый ключ сохранен в файл: {KEY_FILE}")
  except Exception as e:
    print(f"Ошибка при сохранении ключа в файл: {e}. Ключ не будет сохранен.")
  return key


BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_TYPE = os.getenv("DB_TYPE", "sqlite") # Выбор СУБД ('mysql' или 'sqlite' или 'postgresql'). Значение по умолчанию - sqlite
DB_PORT = os.getenv("DB_PORT")
SQLITE_FILE = os.getenv("SQLITE_FILE", "fin_test_bot.db")
# Получение id админов из .env файла, при отсутствии переменной, вернет пустой список
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",") if admin_id]
MANAGER_TELEGRAM_ID = os.getenv("MANAGER_TELEGRAM_ID")
ENCRIPTION_KEY = load_key()
