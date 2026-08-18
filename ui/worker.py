"""
Background worker threads for PowerPoint extraction and document generation.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from core.ai_client import AIClient, AIClientError
from core.config import ConfigError
from core.ppt_reader import extract_text, summarize, PptReadError
from core.router import Router, RunResult, save_state
from ui import i18n


class ExtractionWorker(QThread):
    """Parses text from a PowerPoint (.pptx) file off the UI thread."""

    finished = pyqtSignal(str, str)  # (extracted_text, summary_str)
    error = pyqtSignal(str)

    def __init__(self, file_path: Path, parent=None) -> None:
        super().__init__(parent)
        self._file_path = file_path

    def run(self) -> None:
        try:
            text = extract_text(self._file_path)
            summary = summarize(text)
            self.finished.emit(text, summary)
        except PptReadError as exc:
            self.error.emit(str(exc))
        except Exception as exc:
            self.error.emit(i18n.t("worker_extract_error", exc=exc))


class GenerationWorker(QThread):
    """Runs in-memory document generation off the UI thread. No disk files created."""

    progress = pyqtSignal(int, str)  # (percent, status_message)
    log = pyqtSignal(str)            # log message
    finished = pyqtSignal(object)    # RunResult
    error = pyqtSignal(str)          # error message

    def __init__(
        self,
        source_text: str,
        selections: list[str],
        source_path: Path | None = None,
        db_path: Path | None = None,
        state_path: Path | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._source_text = source_text
        self._selections = selections
        self._source_path = source_path
        self._db_path = db_path
        self._state_path = state_path

    def run(self) -> None:
        try:
            self.progress.emit(10, i18n.t("worker_ai_connecting"))
            self.log.emit(i18n.t("worker_ai_connecting_log"))
            client = AIClient()
            client.check_ready()
            self.log.emit(i18n.t("worker_ai_connected_log"))

            def on_router_progress(msg: str):
                self.log.emit(f"▶ {msg}")

            self.progress.emit(35, i18n.t("worker_generating"))
            router = Router(client, progress=on_router_progress)
            result = router.run_in_memory(
                self._source_text,
                self._selections,
                source_path=self._source_path,
                db_path=self._db_path,
            )

            self.progress.emit(100, i18n.t("worker_generation_done"))
            for doc_name in self._selections:
                self.log.emit(i18n.t("worker_doc_done_log", doc=result.documents[doc_name].display_name_ja))

            # Persist the raw text/data (never a .docx/.xlsx) so reopening
            # this project can show the output again.
            if self._state_path is not None:
                try:
                    save_state(self._state_path, result, self._selections)
                except OSError as exc:
                    self.log.emit(i18n.t("worker_save_internal_error", exc=exc))

            self.finished.emit(result)

        except ConfigError as exc:
            self.error.emit(i18n.t("worker_config_error", exc=exc))
        except AIClientError as exc:
            self.error.emit(i18n.t("worker_ai_error", exc=exc))
        except Exception as exc:
            self.error.emit(i18n.t("worker_unexpected_error", exc_type=type(exc).__name__, exc=exc))
