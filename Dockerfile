     # Используем официальный образ Python
     FROM python:3.13-slim-bullseye

     # Устанавливаем рабочую директорию
     WORKDIR /app

     # Копируем файлы проекта в контейнер
     COPY . .

     # Устанавливаем зависимости
     RUN pip install --no-cache-dir -r requirements.txt

     # Команда для запуска бота
     CMD ["python3", "bot.py"]

