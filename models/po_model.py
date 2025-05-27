from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
import polib
from typing import List

class POTableModel(QAbstractTableModel):
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.po_file = None
        self.entries: List[polib.POEntry] = []
        self.load_po_file()

    def load_po_file(self):
        try:
            self.po_file = polib.pofile(self.file_path, wrapwidth=0, check_for_duplicates=False)
            self.entries = list(self.po_file)
        except Exception as e:
            print(f"Error loading PO file: {e}")

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.entries)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 2

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        row = index.row()
        col = index.column()
        entry = self.entries[row]
        return entry.msgid if col == 0 else entry.msgstr or ""

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return None
        return ["Original Text", "Translation"][section]

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole or not index.isValid() or index.column() != 1:
            return False
        self.entries[index.row()].msgstr = value
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | (Qt.ItemIsEditable if index.column() == 1 else 0)

    def save(self, file_path: str):
        if self.po_file:
            self.po_file.save(file_path)