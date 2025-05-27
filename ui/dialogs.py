from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QTableView
from PySide6.QtGui import QFont
from models.po_model import POTableModel

class ContextDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Translation Context")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        self.context_input = QTextEdit()
        self.context_input.setPlaceholderText("Example: WordPress plugin for gallery management")
        self.context_input.setFont(QFont("Arial", 12))
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        layout.addWidget(QLabel("File Context:"))
        layout.addWidget(self.context_input)
        layout.addWidget(save_button)
        self.setLayout(layout)

class RetryDialog(QDialog):
    def __init__(self, failed_entries, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Translation Errors")
        self.setMinimumSize(600, 400)
        self.failed_entries = failed_entries
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"{len(failed_entries)} entries failed. Retry?"))
        self.table = QTableView()
        self.table_model = POTableModel(self.failed_entries[0][0].po_file.filepath if failed_entries else "")
        self.table.setModel(self.table_model)
        self.table.horizontalHeader().setSectionResizeMode(1)
        self.table.setFont(QFont("Arial", 12))
        layout.addWidget(self.table)
        buttons = QHBoxLayout()
        retry = QPushButton("Retry")
        retry.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(retry)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)
        self.setLayout(layout)