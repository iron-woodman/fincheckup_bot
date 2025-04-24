## -*- coding: utf-8 -*-

from app.utils.encripter import encrypt_message, decrypt_message
from app.config import ENCRIPTION_KEY

if __name__ == "__main__":
    # Пример использования
    message = "ivanov@mail.ru"


    # Зашифровать сообщение
    encrypted_message = encrypt_message(message, ENCRIPTION_KEY)
    print(f"Зашифрованное сообщение: {encrypted_message}")

    # Дешифровать сообщение
    decrypted_message = decrypt_message(encrypted_message, ENCRIPTION_KEY)
    print(f"Расшифрованное сообщение: {decrypted_message}")

    # Убедитесь, что сообщение расшифровано правильно
    assert message == decrypted_message
    print("Все работает правильно!")


