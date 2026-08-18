"""
Document Output screen (popup).

Opens when the user clicks a generated document card. Shows the document as
plain, editable text -- like a notepad -- with exactly one action button:

    📤 Export  -- write the current text out to a real .docx/.xlsx file

Nothing is written to disk unless Export is clicked. Export always uses
whatever text is currently in the box, so there's no separate "save" step --
edit, then export when you're happy with it.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from builders import press_release_builder
from core import missing_tracker
from core.router import ACTION_PLAN, APPROVAL, PRESS_RELEASE, GeneratedDocument, Router
from ui import i18n, theme
from ui.alerts import ModernAlertBox


class DocumentPreviewModal(QDialog):
    """Editable, notepad-style output screen for one generated document."""

    def __init__(
        self,
        doc: GeneratedDocument,
        parent=None,
        default_dir: Path | None = None,
        db_path: Path | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._doc = doc
        self._default_dir = default_dir
        self._db_path = db_path
        lang = i18n.get_language()
        doc_title = doc.display_name_ja if lang == i18n.LANG_JA else doc.display_name_en
        self.resize(860, 680)
        self.setMinimumSize(640, 480)
        self._build_ui(doc_title)

    def _build_ui(self, doc_title: str) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self._container = QFrame()
        self._container.setObjectName("sectionCard")
        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(14)
        
        outer_layout.addWidget(self._container)

        # ── Header ──
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_lbl = QLabel(f"📄  {doc_title}")
        title_lbl.setObjectName("appTitle")
        header_layout.addWidget(title_lbl)

        self._badge = QLabel()
        header_layout.addWidget(self._badge)
        self._update_badge()

        header_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setObjectName("iconBtn")
        close_btn.setFixedSize(34, 34)
        close_btn.setToolTip(i18n.t("editor_close_tooltip"))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Note for structured documents: editing here doesn't change the
        # exported .docx/.xlsx, only the on-screen preview text.
        if self._doc.kind in (APPROVAL, ACTION_PLAN):
            note_lbl = QLabel(i18n.t("editor_structured_note"))
            note_lbl.setObjectName("mutedText")
            note_lbl.setWordWrap(True)
            layout.addWidget(note_lbl)

        # ── Editable Text (notepad-style) ──
        self._text_view = QTextEdit()
        self._text_view.setObjectName("editorText")
        self._text_view.setFont(QFont("Cascadia Code", 13))
        self._text_view.setPlainText(self._doc.preview_text)
        layout.addWidget(self._text_view, stretch=1)

        # ── Missing / Required Items (resolve in place) ──
        self._missing_section = QWidget()
        missing_v = QVBoxLayout(self._missing_section)
        missing_v.setContentsMargins(0, 0, 0, 0)
        missing_v.setSpacing(6)

        missing_heading = QLabel(f"📋  {i18n.t('missing_tab_title')}")
        missing_heading.setObjectName("sectionHeading")
        missing_v.addWidget(missing_heading)

        missing_desc = QLabel(i18n.t("missing_desc"))
        missing_desc.setObjectName("secondaryText")
        missing_desc.setWordWrap(True)
        missing_v.addWidget(missing_desc)

        self._missing_list = QListWidget()
        self._missing_list.setObjectName("missingItemsList")
        self._missing_list.setMaximumHeight(140)
        self._missing_list.itemClicked.connect(self._on_missing_item_clicked)
        missing_v.addWidget(self._missing_list)

        layout.addWidget(self._missing_section)
        self._refresh_missing_list()

        # ── Footer: the single Export action ──
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        export_btn = QPushButton("📤")
        export_btn.setObjectName("iconBtnPrimary")
        export_btn.setFixedSize(48, 48)
        export_btn.setToolTip(i18n.t("editor_export_tooltip"))
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self._on_export)
        footer_layout.addWidget(export_btn)

        layout.addLayout(footer_layout)

    def _refresh_missing_list(self) -> None:
        self._missing_list.clear()
        dark = theme.is_dark()
        red_color = "#F87171" if dark else "#DC2626"
        green_color = "#34D399" if dark else "#16A34A"
        for mi in self._doc.missing_items:
            if mi.resolved:
                text = f"🟢 {mi.field}" + (f" — {mi.context}" if mi.context else "")
                color = green_color
            else:
                text = f"🔴 {mi.field}" + (f" — {mi.context}" if mi.context else "")
                color = red_color
            list_item = QListWidgetItem(text)
            list_item.setForeground(QColor(color))
            list_item.setData(Qt.ItemDataRole.UserRole, mi)
            self._missing_list.addItem(list_item)
        self._missing_section.setVisible(bool(self._doc.missing_items))

    def _on_missing_item_clicked(self, list_item: QListWidgetItem) -> None:
        mi = list_item.data(Qt.ItemDataRole.UserRole)
        if mi is None or mi.id is None or self._db_path is None:
            return  # nothing persistable to toggle (e.g. no DB id yet)
        mi.resolved = not mi.resolved
        missing_tracker.resolve_item(mi.id, resolved=mi.resolved, db_path=self._db_path)
        self._refresh_missing_list()
        self._update_badge()

    def _update_badge(self) -> None:
        lang = i18n.get_language()
        missing_count = sum(1 for mi in self._doc.missing_items if not mi.resolved)
        if missing_count > 0:
            self._badge.setText(f"⚠ 要確認項目: {missing_count}件" if lang == "ja" else f"⚠ Pending: {missing_count}")
            self._badge.setObjectName("badgeWarning")
        else:
            self._badge.setText("✓ 内容確定済" if lang == "ja" else "✓ Complete")
            self._badge.setObjectName("badgeSuccess")
        self._badge.style().unpolish(self._badge)
        self._badge.style().polish(self._badge)

    def _on_export(self) -> None:
        # Export always reflects whatever is currently in the text box. For
        # the Press Release, that text *is* the document, so sync it back
        # onto the in-memory doc (and recompute its missing-item count)
        # before writing the file -- no separate save step needed.
        if self._doc.kind == PRESS_RELEASE:
            new_text = self._text_view.toPlainText()
            self._doc.preview_text = new_text
            self._doc.raw_data = new_text
            # Re-detected items are fresh objects with no DB id, so anything
            # resolved above can't be re-resolved until the next full
            # generation -- same limitation export already had before resolve
            # tracking existed, just now visible in the list too.
            self._doc.missing_items = press_release_builder.detect_missing(new_text)
            for item in self._doc.missing_items:
                item.output = self._doc.display_name_ja
            self._refresh_missing_list()
            self._update_badge()

        ext = ".xlsx" if self._doc.kind == ACTION_PLAN else ".docx"
        file_filter = "Excel (*.xlsx)" if ext == ".xlsx" else "Word (*.docx)"
        default_name = f"{self._doc.source_stem}_{self._doc.kind}{ext}"
        start_dir = self._default_dir if self._default_dir and self._default_dir.is_dir() else Path.home()

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            i18n.t("export_btn"),
            str(start_dir / default_name),
            file_filter,
        )
        if not save_path:
            return

        lang = i18n.get_language()
        saved_path = Path(save_path)
        try:
            Router.export_document(self._doc, saved_path)
            ModernAlertBox.information(
                self,
                i18n.t("export_complete"),
                i18n.t("export_success_msg", file=saved_path.name),
            )
        except Exception as exc:
            ModernAlertBox.critical(
                self,
                i18n.t("export_error"),
                i18n.t("export_fail_msg", exc=exc),
            )
