from PySide6.QtWidgets import QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QComboBox, QLineEdit, QTextEdit, QProgressBar, QLabel, QCheckBox, QTableView, QGroupBox, QFormLayout, QTabWidget
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from core.file_manager import FileManager
from core.api_manager import APIManager
from core.translator import TranslationThread
from core.settings import SettingsManager
from core.logger import Logger
from ui.dialogs import ContextDialog, RetryDialog
from ui.styles import StyleManager
from models.po_model import POTableModel
from models.api_models import APIModels
import os
import asyncio

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PO Translator")
        self.setMinimumSize(960, 700)
        self.setAcceptDrops(True)
        self.file_manager = FileManager()
        self.settings = SettingsManager()
        self.logger = Logger()
        self.style_manager = StyleManager()
        self.translation_thread = None
        self.po_model = None
        self.context = ""
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Left Panel: Controls
        left_layout = QVBoxLayout()
        
        # Controls Group
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        self.select_button = QPushButton("Select .po File")
        self.select_button.clicked.connect(self.select_file)
        select_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons", "select_file.svg")
        if os.path.exists(select_icon_path):
            self.select_button.setIcon(QIcon(select_icon_path))
        self.select_button.setIconSize(QSize(24, 24))
        
        self.theme_button = QPushButton()
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.update_theme_icon()
        file_action_layout = QHBoxLayout()
        file_action_layout.addWidget(self.select_button)
        file_action_layout.addWidget(self.theme_button)
        controls_layout.addLayout(file_action_layout)

        # Tabs
        tabs = QTabWidget()
        
        # API Settings Tab
        api_tab = QWidget()
        api_layout = QFormLayout()
        self.api_service_combo = QComboBox()
        self.api_service_combo.addItems(["OpenRouter.ai", "Google Gemini"])
        self.api_service_combo.currentIndexChanged.connect(self.on_api_service_changed)
        self.model_combo = QComboBox()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.textChanged.connect(self.validate_api_key_input)
        self.test_key_button = QPushButton("Test Key")
        self.test_key_button.clicked.connect(self.test_api_key)
        self.key_status_label = QLabel("")
        self.show_api_key_checkbox = QCheckBox("Show Key")
        self.show_api_key_checkbox.stateChanged.connect(self.toggle_api_key_visibility)
        self.save_api_key_checkbox = QCheckBox("Save Key")
        self.save_api_key_checkbox.setChecked(True)
        api_layout.addRow("API Service:", self.api_service_combo)
        api_layout.addRow("Model:", self.model_combo)
        api_layout.addRow("API Key:", self.api_key_input)
        api_layout.addRow("", self.test_key_button)
        api_layout.addRow("", self.key_status_label)
        api_layout.addRow("", self.show_api_key_checkbox)
        api_layout.addRow("", self.save_api_key_checkbox)
        api_tab.setLayout(api_layout)
        tabs.addTab(api_tab, "API Settings")

        # Translation Settings Tab
        trans_tab = QWidget()
        trans_layout = QFormLayout()
        self.language_combo = QComboBox()
        self.language_combo.addItem("English (en)", "en")
        self.language_combo.addItem("Persian (fa)", "fa")
        self.language_combo.addItem("Arabic (ar)", "ar")
        self.translate_placeholders_checkbox = QCheckBox("Translate Sentences with Variables")
        self.overwrite_checkbox = QCheckBox("Overwrite Existing Translations")
        context_button = QPushButton("Set Context")
        context_button.clicked.connect(self.open_context_dialog)
        trans_layout.addRow("Target Language:", self.language_combo)
        trans_layout.addRow("", self.translate_placeholders_checkbox)
        trans_layout.addRow("", self.overwrite_checkbox)
        trans_layout.addRow("", context_button)
        trans_tab.setLayout(trans_layout)
        tabs.addTab(trans_tab, "Translation Settings")

        controls_layout.addWidget(tabs)
        controls_group.setLayout(controls_layout)
        left_layout.addWidget(controls_group)

        # Action Buttons
        action_layout = QHBoxLayout()
        self.translate_button = QPushButton("Start Translation")
        self.translate_button.clicked.connect(self.translate_file)
        self.translate_button.setEnabled(False)
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_translation)
        self.pause_button.setEnabled(False)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_translation)
        self.stop_button.setEnabled(False)
        action_layout.addWidget(self.translate_button)
        action_layout.addWidget(self.pause_button)
        action_layout.addWidget(self.stop_button)
        left_layout.addLayout(action_layout)

        # Progress Group
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("%p%")
        self.status_summary = QLabel("Total: 0 | Translated: 0 | ETA: 0s")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_summary)
        progress_group.setLayout(progress_layout)
        left_layout.addWidget(progress_group)

        # Log Group
        log_group = QGroupBox("Operation Log")
        log_layout = QVBoxLayout()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.logger.set_ui_handler(self.log_box.append)
        clear_log_button = QPushButton("Clear Log")
        clear_log_button.clicked.connect(self.log_box.clear)
        log_layout.addWidget(self.log_box)
        log_layout.addWidget(clear_log_button)
        log_group.setLayout(log_layout)
        left_layout.addWidget(log_group)

        # Right Panel: Preview
        right_layout = QVBoxLayout()
        preview_group = QGroupBox("Translation Preview")
        preview_layout = QVBoxLayout()
        self.preview_table = QTableView()
        self.preview_table.horizontalHeader().setSectionResizeMode(1)
        preview_layout.addWidget(self.preview_table)
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        self.setStyleSheet(self.style_manager.get_stylesheet())
        self.on_api_service_changed()

    def update_theme_icon(self):
        icon_name = "moon.svg" if self.style_manager.theme == "dark" else "sun.svg"
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons", icon_name)
        if os.path.exists(icon_path):
            self.theme_button.setIcon(QIcon(icon_path))
        else:
            self.theme_button.setText("Theme")
        self.theme_button.setIconSize(QSize(24, 24))

    def toggle_theme(self):
        self.style_manager.theme = "light" if self.style_manager.theme == "dark" else "dark"
        self.update_theme_icon()
        self.setStyleSheet(self.style_manager.get_stylesheet())
        self.settings.save_setting("theme", self.style_manager.theme)

    def toggle_api_key_visibility(self):
        self.api_key_input.setEchoMode(QLineEdit.Normal if self.show_api_key_checkbox.isChecked() else QLineEdit.Password)

    def validate_api_key_input(self):
        api_key = self.api_key_input.text().strip()
        self.key_status_label.setText("No API key provided" if not api_key else "")
        self.test_key_button.setEnabled(bool(api_key))

    def test_api_key(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.logger.log("No API key provided", "error")
            return
        service = "openrouter" if self.api_service_combo.currentIndex() == 0 else "gemini"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_manager = APIManager(service, api_key)
        is_valid, message = loop.run_until_complete(api_manager.validate_api_key())
        self.key_status_label.setText(message)
        self.logger.log(f"{'✅' if is_valid else '❌'} {message}")
        loop.close()

    def on_api_service_changed(self):
        service = "openrouter" if self.api_service_combo.currentIndex() == 0 else "gemini"
        self.model_combo.clear()
        self.model_combo.addItems([name for name, _ in APIModels.get_models(service)])
        api_key = self.settings.load_api_key(service)
        self.api_key_input.setText(api_key)
        self.save_api_key_checkbox.setChecked(bool(api_key))
        self.validate_api_key_input()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PO File", "", "PO Files (*.po)")
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        success, message = self.file_manager.load_file(file_path)
        self.logger.log(message)
        if success:
            self.po_model = POTableModel(file_path)
            self.preview_table.setModel(self.po_model)
            self.translate_button.setEnabled(True)
            self.status_summary.setText(f"Total: {len(self.file_manager.get_entries())} | Translated: 0 | ETA: 0s")
            self.progress_bar.setValue(0)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.po'):
                self.load_file(file_path)
            else:
                self.logger.log(f"File '{file_path}' must be a .po file", "error")

    def translate_file(self):
        if not self.file_manager.po_file or not self.api_key_input.text().strip():
            self.logger.log("Select a .po file and enter an API key", "error")
            return
        service = "openrouter" if self.api_service_combo.currentIndex() == 0 else "gemini"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_manager = APIManager(service, self.api_key_input.text().strip())
        is_valid, message = loop.run_until_complete(api_manager.validate_api_key())
        loop.close()
        if not is_valid:
            self.logger.log("Invalid API key", "error")
            return

        self.translate_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.translation_thread = TranslationThread(
            self.file_manager.po_file.filepath, self.language_combo.currentData() or "en",
            self.api_key_input.text().strip(), APIModels.get_models(service)[self.model_combo.currentIndex()][1],
            service, self.context, self.overwrite_checkbox.isChecked(), self.translate_placeholders_checkbox.isChecked()
        )
        self.translation_thread.progress.connect(self.progress_bar.setValue)
        self.translation_thread.log.connect(self.logger.log)
        self.translation_thread.finished.connect(self.translation_finished)
        self.translation_thread.preview.connect(self.update_preview)
        self.translation_thread.start()

    def pause_translation(self):
        if self.translation_thread:
            self.translation_thread.running = False  # Pause by stopping the loop
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.logger.log("Translation paused")

    def stop_translation(self):
        if self.translation_thread:
            self.translation_thread.running = False
            self.translation_thread.terminate()
            self.translation_thread.wait()
            self.translate_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.logger.log("Translation stopped")

    def update_preview(self, row: int, original: str, translation: str):
        if self.po_model:
            index = self.po_model.index(row, 1)
            self.po_model.setData(index, translation, Qt.EditRole)

    def translation_finished(self, output_file: str, failed_entries: list):
        self.translate_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100)
        if output_file:
            self.po_model.save(output_file)
            self.logger.log(f"Translation saved at {output_file}")
        if failed_entries:
            dialog = RetryDialog(failed_entries, self)
            if dialog.exec():
                self.translation_thread = TranslationThread(
                    self.file_manager.po_file.filepath, self.language_combo.currentData() or "en",
                    self.api_key_input.text().strip(), APIModels.get_models("openrouter" if self.api_service_combo.currentIndex() == 0 else "gemini")[self.model_combo.currentIndex()][1],
                    "openrouter" if self.api_service_combo.currentIndex() == 0 else "gemini", self.context,
                    self.overwrite_checkbox.isChecked(), self.translate_placeholders_checkbox.isChecked()
                )
                self.translation_thread.progress.connect(self.progress_bar.setValue)
                self.translation_thread.log.connect(self.logger.log)
                self.translation_thread.finished.connect(self.translation_finished)
                self.translation_thread.preview.connect(self.update_preview)
                self.translation_thread.start()

    def open_context_dialog(self):
        dialog = ContextDialog(self)
        dialog.context_input.setPlainText(self.context)
        if dialog.exec():
            self.context = dialog.context_input.toPlainText()
            self.settings.save_setting("context", self.context)
            self.logger.log("Context updated")

    def load_settings(self):
        self.style_manager.theme = self.settings.load_setting("theme", "dark")
        self.setStyleSheet(self.style_manager.get_stylesheet())
        self.update_theme_icon()
        service_idx = self.settings.load_setting("api_service_index", 0, int)
        self.api_service_combo.setCurrentIndex(service_idx)
        self.on_api_service_changed()
        lang = self.settings.load_setting("language", "en", str)
        for idx in range(self.language_combo.count()):
            if self.language_combo.itemData(idx) == lang:
                self.language_combo.setCurrentIndex(idx)
                break
        self.translate_placeholders_checkbox.setChecked(self.settings.load_setting("translate_placeholders", False, bool))
        self.overwrite_checkbox.setChecked(self.settings.load_setting("overwrite_translations", False, bool))
        self.context = self.settings.load_setting("context", "", str)

    def closeEvent(self, event):
        if self.translation_thread and self.translation_thread.isRunning():
            self.translation_thread.running = False
            self.translation_thread.terminate()
            self.translation_thread.wait()
        event.accept()