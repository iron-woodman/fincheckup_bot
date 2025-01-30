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
