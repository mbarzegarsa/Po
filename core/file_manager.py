import polib
from typing import List, Tuple

class FileManager:
    def __init__(self):
        self.po_file = None
        self.entries: List[polib.POEntry] = []

    def load_file(self, file_path: str) -> Tuple[bool, str]:
        try:
            self.po_file = polib.pofile(file_path, wrapwidth=0, check_for_duplicates=False)
            self.entries = list(self.po_file)
            return True, f"Loaded {len(self.entries)} entries"
        except Exception as e:
            return False, f"Error loading file: {str(e)}"

    def save_translated(self, output_path: str) -> bool:
        if not self.po_file:
            return False
        try:
            self.po_file.save(output_path)
            return True
        except Exception:
            return False

    def get_entries(self) -> List[polib.POEntry]:
        return self.entries