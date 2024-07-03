from decouple import config
from cryptography.fernet import Fernet


class EncryptionHelper:
    f = None

    def __init__(self):
        key: bytes = bytes(config("ACCOUNTS_ENCRYPTION_KEY"), "ascii")
        self.f = Fernet(key)

    def encrypt(self, data: bytes):
        stringBytes = bytes(data, "UTF-8")
        encr = self.f.encrypt(stringBytes)
        return encr

    def decrypt(self, data: bytes):
        return self.f.decrypt(b"" + data).decode("UTF-8")
