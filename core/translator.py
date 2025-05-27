from PySide6.QtCore import QThread, pyqtSignal
import polib
import asyncio
from typing import List, Tuple
from core.api_manager import APIManager

class TranslationThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(str, list)
    preview = pyqtSignal(int, str, str)

    def __init__(self, file_path: str, dest_language: str, api_key: str, model: str, service: str, context: str = "", 
                 overwrite: bool = False, translate_placeholders: bool = False, use_proxy: bool = False):
        super().__init__()
        self.file_path = file_path
        self.dest_language = dest_language
        self.api_key = api_key
        self.model = model
        self.service = service
        self.context = context
        self.overwrite = overwrite
        self.translate_placeholders = translate_placeholders
        self.use_proxy = use_proxy
        self.api = APIManager(service, api_key, use_proxy)
        self.running = False
        self.failed_entries: List[Tuple[polib.POEntry, str]] = []

    async def translate_chunk(self, chunk: List[polib.POEntry], chunk_idx: int, total_chunks: int, chunk_size: int, total: int):
        translated_count = 0
        for i, entry in enumerate(chunk):
            if not self.running:
                break
            entry_idx = (chunk_idx - 1) * chunk_size + i
            if not entry.msgid.strip():
                entry.msgstr = entry.msgid
                self.log.emit("ℹ️ Empty text")
                continue
            if not self.overwrite and entry.msgstr.strip():
                self.log.emit(f"⏩ Skipped '{entry.msgid}' (unchanged)")
                continue
            if re.search(r'%[sd]|%[0-9]\$[sd]|\{[0-9]+\}|\{[^{}]*?\}|\<[^>]+?\>|\[[^\]]+?\]', entry.msgid) and not self.translate_placeholders:
                self.log.emit(f"⏩ Skipped '{entry.msgid}' due to variables")
                continue

            self.log.emit(f"🔄 Translating '{entry.msgid}'...")
            translated = await self.api.translate_text(entry.msgid, self.dest_language, self.model, self.context)
            entry.msgstr = translated
            self.log.emit(f"✅ Translated: '{translated}'")
            self.preview.emit(entry_idx, entry.msgid, translated)
            translated_count += 1
            self.progress.emit(int((entry_idx + 1) / total * 100))
            await asyncio.sleep(0.2)

        return translated_count

    def run(self):
        self.running = True
        self.failed_entries = []
        self.log.emit("🚀 Translation started...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            po = polib.pofile(self.file_path, wrapwidth=0, check_for_duplicates=False)
            total = len(po)
            chunk_size = max(1, min(10, total // 10 + 1))
            chunks = [po[i:i + chunk_size] for i in range(0, total, chunk_size)]
            output_file = self.file_path.replace('.po', '_translated.po')
            translated_count = 0

            for chunk_idx, chunk in enumerate(chunks, 1):
                if not self.running:
                    break
                self.log.emit(f"🔄 Processing chunk {chunk_idx}/{len(chunks)}...")
                translated_count += loop.run_until_complete(self.translate_chunk(chunk, chunk_idx, len(chunks), chunk_size, total))

            if self.running:
                po.save(output_file)
                self.log.emit(f"💾 Translated file saved at {output_file}")
                self.finished.emit(output_file, self.failed_entries)
            else:
                self.log.emit("⛔ Translation stopped")
                self.finished.emit("", self.failed_entries)
        except Exception as e:
            self.log.emit(f"❌ Error: {str(e)}")
            self.finished.emit("", self.failed_entries)
        finally:
            self.running = False
            loop.close()