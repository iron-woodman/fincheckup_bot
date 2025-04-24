import asyncio
from cryptography.fernet import Fernet
import base64


async def encrypt_message(message: str, key: bytes) -> str:
  """Шифрует сообщение с использованием AES."""
  f = Fernet(key)
  encrypted_message = f.encrypt(message.encode('utf-8'))
  return base64.b64encode(encrypted_message).decode('utf-8')

async def decrypt_message(encrypted_message: str, key: bytes) -> str:
  """Дешифрует сообщение, зашифрованное AES."""
  f = Fernet(key)
  encrypted_message_bytes = base64.b64decode(encrypted_message.encode('utf-8'))
  decrypted_message = f.decrypt(encrypted_message_bytes).decode('utf-8')
  return decrypted_message
