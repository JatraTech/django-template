from django.conf import settings
import base64
import hashlib
from cryptography.fernet import Fernet


def get_fernet():
    secret = settings.SECRET_KEY.encode()
    key = hashlib.sha256(secret).digest()[:32]  # truncate to 32 bytes
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)


_fernet = get_fernet()


def encrypt_text(txt: str) -> bytes:
    return _fernet.encrypt(txt.encode())


def decrypt_text(ciphertext: bytes) -> str:
    txt = _fernet.decrypt(ciphertext).decode()
    return txt
