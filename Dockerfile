     # Используем официальный образ Python
     FROM python

     # Устанавливаем рабочую директорию
     WORKDIR /app

     # Копируем файлы проекта в контейнер
     COPY . .

     # Устанавливаем зависимости
     RUN pip install --no-cache-dir -r requirements.txt

     # Команда для запуска бота
     CMD ["python3", "bot.py"]

