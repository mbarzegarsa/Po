import logging
from datetime import datetime

class Logger:
    def __init__(self, log_file: str = "translator.log"):
        self.logger = logging.getLogger("TranslatorApp")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Stream handler for UI
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(formatter)
        self.logger.addHandler(self.stream_handler)

    def log(self, message: str, level: str = "info"):
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)

    def set_ui_handler(self, ui_callback):
        """Set a callback to send logs to UI."""
        self.stream_handler.stream = ui_callback