from cryptography.fernet import Fernet
import base64
from django.conf import settings

def get_cipher():
    key = settings.SECRET_KEY.encode('utf-8')[:32].ljust(32, b'0')
    return Fernet(base64.urlsafe_b64encode(key))

def encrypt(text: str) -> str:
    if not text:
        return text
    cipher_suite = get_cipher()
    encrypted_text = cipher_suite.encrypt(text.encode('utf-8'))
    return encrypted_text.decode('utf-8')

def decrypt(encrypted_text: str) -> str:
    if not encrypted_text:
        return encrypted_text
    cipher_suite = get_cipher()
    try:
        decrypted_text = cipher_suite.decrypt(encrypted_text.encode('utf-8'))
        return decrypted_text.decode('utf-8')
    except Exception:
        return ""
