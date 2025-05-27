from PySide6.QtCore import QSettings
from cryptography.fernet import Fernet
import os

class SettingsManager:
    def __init__(self):
        self.settings = QSettings("MyApp", "Translator")
        self.key_file = "encryption.key"
        self.cipher = self._load_cipher()

    def _load_cipher(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        with open(self.key_file, "rb") as f:
            key = f.read()
        return Fernet(key)

    def save_api_key(self, service: str, api_key: str, save_enabled: bool = True) -> bool:
        if not save_enabled or not api_key:
            return False
        encrypted_key = self.cipher.encrypt(api_key.strip().encode()).decode()
        self.settings.setValue(f"api_key_{service}", encrypted_key)
        return True

    def load_api_key(self, service: str) -> str:
        encrypted_key = self.settings.value(f"api_key_{service}", "", str)
        if not encrypted_key:
            return ""
        try:
            return self.cipher.decrypt(encrypted_key.encode()).decode()
        except:
            return ""

    def clear_api_key(self, service: str):
        self.settings.remove(f"api_key_{service}")

    def save_setting(self, key: str, value):
        self.settings.setValue(key, value)

    def load_setting(self, key: str, default_value):
        return self.settings.value(key, default_value)