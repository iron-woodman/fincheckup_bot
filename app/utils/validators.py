## -*- coding: utf-8 -*-

import re

# Шаблонные регулярные выражения
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PHONE_REGEX = r"^\+?[1-9]\d{1,14}$"  # Пример для международного формата, можете адаптировать под свои нужды

def validate_email(email: str) -> bool:
    """
    Проверяет, является ли строка корректным email-адресом.

    Args:
        email: Строка для проверки.

    Returns:
        True, если строка является валидным email, иначе False.
    """
    if not isinstance(email, str):
        return False
    return bool(re.match(EMAIL_REGEX, email))


def validate_phone(phone: str) -> bool:
    """
    Проверяет, является ли строка корректным номером телефона.

    Args:
        phone: Строка для проверки.

    Returns:
        True, если строка является валидным номером телефона, иначе False.
    """
    if not isinstance(phone, str):
        return False
    return bool(re.match(PHONE_REGEX, phone))

def validate_age(age: str) -> bool:
    """
    Проверяет, является ли строка корректным возрастом (целое положительное число).
    Args:
        age: Строка для проверки

    Returns:
        True, если строка является валидным возрастом, иначе False.
    """
    if not isinstance(age, str):
        return False
    try:
        age = int(age)
        return 100 > age > 10
    except ValueError:
        return False

def validate_children_count(count: str) -> bool:
    """
    Проверяет, является ли строка корректным количеством детей (неотрицательное целое число).

    Args:
        count: Строка для проверки.

    Returns:
        True, если строка является валидным количеством детей, иначе False.
    """
    if not isinstance(count, str):
      return False
    try:
        count = int(count)
        return count >= 0
    except ValueError:
        return False


def validate_full_name(full_name: str) -> bool:
    """
    Проверяет, является ли введенное имя корректным.

    Args:
        full_name (str): Полное имя пользователя.

    Returns:
        bool: True, если имя корректно, иначе False.
    """
    if not full_name:
        return False  # Имя не может быть пустым

    # Регулярное выражение для проверки:
    # ^ - начало строки
    # [A-Za-zА-Яа-яёЁ\s\-] - любой символ из букв, пробелов или дефисов
    # + - как минимум один символ должен быть в имени
    # $ - конец строки
    pattern = r"^[A-Za-zА-Яа-яёЁ\s\-]+$"

    if not re.match(pattern, full_name):
        return False  # Если имя содержит невалидные символы

    return True # если все проверки пройдены имя корректно


def validate_city_name(city_name: str) -> bool:
    """
    Проверяет, является ли введенное название города корректным.

    Args:
        city_name (str): Название города.

    Returns:
        bool: True, если название города корректно, иначе False.
    """
    if not city_name:
        return False  # Название города не может быть пустым

    # Регулярное выражение для проверки:
    # ^ - начало строки
    # [A-Za-zА-Яа-яёЁ\s\-\'] - любой символ из букв, пробелов, дефисов или апострофов
    # + - как минимум один символ должен быть в названии города
    # $ - конец строки
    pattern = r"^[A-Za-zА-Яа-яёЁ\s\-\']+$"
    if not re.match(pattern, city_name):
        return False  # Если название города содержит невалидные символы

    return True  # Если все проверки пройдены, название города корректно


def validate_user_status(user_status: str) -> bool:
    """
    Проверяет, является ли введенный статус пользователя корректным.

    Args:
        user_status (str): Статус пользователя в Германии.

    Returns:
        bool: True, если статус корректный, иначе False.
    """
    if not user_status:
        return False  # Статус не может быть пустым

    # На данном этапе мы просто проверяем, что строка не пустая
    # Можно добавить дополнительные проверки по необходимости
    # Например, проверять на соответствие списку допустимых значений
    # или проверять наличие определенных слов в строке, если необходимо

    return True # если все проверки пройдены, статус корректен





if __name__ == '__main__':
    # Примеры использования
    print(f"Valid email: {validate_email('test@example.com')}")       # True
    print(f"Invalid email: {validate_email('invalid_email')}")       # False
    print(f"Valid phone: {validate_phone('+15551234567')}")           # True
    print(f"Invalid phone: {validate_phone('1234567')}")          # False
    print(f"Valid age: {validate_age('25')}")           # True
    print(f"Invalid age: {validate_age('-5')}")          # False
    print(f"Invalid age: {validate_age('string')}")          # False
    print(f"Valid children count: {validate_children_count('3')}") # True
    print(f"Invalid children count: {validate_children_count('-2')}") # False
    print(f"Invalid children count: {validate_children_count('text')}") # False

    name1 = "Иван Иванов иванович"
    name2 = "Петр-Иванов"
    name3 = "Anna Smith"
    name4 = "Иван123"
    name5 = ""
    name6 = "Иван   Иванов"

    print(f"'{name1}': {validate_full_name(name1)}")  # Выведет: 'Иван Иванов': True
    print(f"'{name2}': {validate_full_name(name2)}")  # Выведет: 'Петр-Иванов': True
    print(f"'{name3}': {validate_full_name(name3)}")  # Выведет: 'Anna Smith': True
    print(f"'{name4}': {validate_full_name(name4)}")  # Выведет: 'Иван123': False
    print(f"'{name5}': {validate_full_name(name5)}")  # Выведет: '': False
    print(f"'{name6}': {validate_full_name(name6)}")  # Выведет: 'Иван   Иванов': True
