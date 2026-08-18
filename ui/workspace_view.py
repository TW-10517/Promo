"""
Unified Promotion Document Generator Workspace.

Features:
- Pure Japanese by default with instantaneous English toggle.
- Dual Theme: Dark Mode and Light Mode with instant toggle button.
- Clean selector-based styling (no hardcoded inline styles).
- In-memory generation: NO Word/Excel files created on disk automatically.
- Interactive output cards: clicking any output pops up the detailed preview modal.
- No clutter (no open project folder, no delete/edit noise).
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core import config
from core.project_manager import Project, ProjectManager
from core.router import (
    ACTION_PLAN,
    APPROVAL,
    PRESS_RELEASE,
    GeneratedDocument,
    RunResult,
    build_legacy_document,
    load_state,
    save_state,
)
from ui import i18n, theme
from ui.alerts import ModernAlertBox
from ui.preview_modal import DocumentPreviewModal
from ui.worker import ExtractionWorker, GenerationWorker


class ClickableCard(QFrame):
    """A QFrame that emits `clicked` when pressed anywhere on it (not just a button)."""

    clicked = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class PromotionGenWorkspace(QWidget):
    """Project-scoped workspace: document generation and preview."""

    back_requested = pyqtSignal()
    project_updated = pyqtSignal(Project)
    language_changed = pyqtSignal()
    theme_changed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._project: Project | None = None
        self._extracted_text: str = ""
        self._selected_file_path: Path | None = None
        self._extraction_worker: ExtractionWorker | None = None
        self._worker: GenerationWorker | None = None
        self._latest_result: RunResult | None = None
        self._setup_visible: bool = True

        self._build_ui()
        self.update_ui_state()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(28, 20, 28, 20)
        outer_layout.setSpacing(16)

        # ═════════════════════════════════════════════════════════
        # 1. Top Header Bar
        # ═════════════════════════════════════════════════════════
        self._top_bar = QFrame()
        self._top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(self._top_bar)
        top_layout.setContentsMargins(20, 14, 20, 14)
        top_layout.setSpacing(16)

        # Back button: goes to the Output view if one exists and we're
        # currently on the generation steps, otherwise goes to the Home
        # screen (see _on_back_clicked).
        self._back_btn = QPushButton()
        self._back_btn.setObjectName("toolBtn")
        self._back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._back_btn.clicked.connect(self._on_back_clicked)
        top_layout.addWidget(self._back_btn)

        # Title & Subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        self._app_title_lbl = QLabel()
        self._app_title_lbl.setObjectName("appTitle")
        title_box.addWidget(self._app_title_lbl)

        self._app_subtitle_lbl = QLabel()
        self._app_subtitle_lbl.setObjectName("appSubtitle")
        title_box.addWidget(self._app_subtitle_lbl)
        top_layout.addLayout(title_box, stretch=1)

        # AI Backend Model Badge
        provider = config.get_provider()
        model_name = config.get_model()
        if provider in {"local", "ollama"}:
            model_text = f"⚡ ローカルAI: Ollama ({model_name})"
            self._model_badge = QLabel(model_text)
            self._model_badge.setObjectName("badgePrimary")
        else:
            model_text = f"🌐 クラウドAI: Claude ({model_name})"
            self._model_badge = QLabel(model_text)
            self._model_badge.setObjectName("badgeSuccess")

        top_layout.addWidget(self._model_badge)

        # Go to the generation steps (only shown while viewing the Output
        # view -- a plain labeled button, not an icon, so its purpose is
        # obvious at a glance).
        self._goto_generate_btn = QPushButton()
        self._goto_generate_btn.setObjectName("toolBtn")
        self._goto_generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._goto_generate_btn.clicked.connect(lambda: self._set_setup_visible(True))
        top_layout.addWidget(self._goto_generate_btn)

        # Theme Toggle Button
        self._theme_btn = QPushButton()
        self._theme_btn.setObjectName("toolBtn")
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self._toggle_theme)
        top_layout.addWidget(self._theme_btn)

        # Language Toggle Button
        self._lang_btn = QPushButton()
        self._lang_btn.setObjectName("toolBtn")
        self._lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._lang_btn.clicked.connect(self._toggle_language)
        top_layout.addWidget(self._lang_btn)

        outer_layout.addWidget(self._top_bar)

        # ═════════════════════════════════════════════════════════
        # Main Scrollable Body
        # ═════════════════════════════════════════════════════════
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._content_widget = QWidget()
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(0, 0, 8, 0)
        content_layout.setSpacing(16)

        # ─────────────────────────────────────────────────────────
        # STEP 1: Planning Document Input Card
        # ─────────────────────────────────────────────────────────
        self._step1_card = QFrame()
        self._step1_card.setObjectName("sectionCardAccent")
        step1_layout = QVBoxLayout(self._step1_card)
        step1_layout.setContentsMargins(22, 18, 22, 18)
        step1_layout.setSpacing(12)

        self._step1_title_lbl = QLabel()
        self._step1_title_lbl.setObjectName("sectionHeading")
        step1_layout.addWidget(self._step1_title_lbl)

        file_picker_row = QHBoxLayout()
        file_picker_row.setSpacing(10)

        self._file_path_edit = QLineEdit()
        self._file_path_edit.setReadOnly(True)
        self._file_path_edit.setMinimumHeight(42)
        file_picker_row.addWidget(self._file_path_edit, stretch=1)

        self._browse_btn = QPushButton()
        self._browse_btn.setObjectName("toolBtn")
        self._browse_btn.setMinimumHeight(42)
        self._browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._browse_btn.clicked.connect(self._on_browse_file)
        file_picker_row.addWidget(self._browse_btn)
        step1_layout.addLayout(file_picker_row)

        self._extract_status_lbl = QLabel()
        self._extract_status_lbl.setObjectName("secondaryText")
        step1_layout.addWidget(self._extract_status_lbl)

        # Slide content preview
        self._preview_edit = QTextEdit()
        self._preview_edit.setObjectName("logConsole")
        self._preview_edit.setReadOnly(True)
        self._preview_edit.setMinimumHeight(90)
        self._preview_edit.setMaximumHeight(130)
        step1_layout.addWidget(self._preview_edit)

        content_layout.addWidget(self._step1_card)

        # ─────────────────────────────────────────────────────────
        # STEP 2: Document Selection & Generate Card
        # ─────────────────────────────────────────────────────────
        self._step2_card = QFrame()
        self._step2_card.setObjectName("sectionCard")
        step2_layout = QVBoxLayout(self._step2_card)
        step2_layout.setContentsMargins(22, 18, 22, 18)
        step2_layout.setSpacing(14)

        self._step2_title_lbl = QLabel()
        self._step2_title_lbl.setObjectName("sectionHeading")
        step2_layout.addWidget(self._step2_title_lbl)

        # 3 Document Toggle Cards
        doc_cards_row = QHBoxLayout()
        doc_cards_row.setSpacing(12)

        self._card_approval, self._btn_approval, self._desc_approval = self._make_doc_toggle_card(
            "doc_approval", "doc_approval_desc", "📝"
        )
        doc_cards_row.addWidget(self._card_approval)

        self._card_action_plan, self._btn_action_plan, self._desc_action_plan = self._make_doc_toggle_card(
            "doc_action_plan", "doc_action_plan_desc", "📊"
        )
        doc_cards_row.addWidget(self._card_action_plan)

        self._card_press, self._btn_press, self._desc_press = self._make_doc_toggle_card(
            "doc_press_release", "doc_press_release_desc", "📰"
        )
        doc_cards_row.addWidget(self._card_press)

        step2_layout.addLayout(doc_cards_row)

        # Action Buttons Row
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self._start_btn = QPushButton()
        self._start_btn.setObjectName("primaryButton")
        self._start_btn.setMinimumHeight(48)
        self._start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_btn.clicked.connect(self._on_start_generation)
        action_row.addWidget(self._start_btn, stretch=1)

        self._cancel_btn = QPushButton()
        self._cancel_btn.setObjectName("dangerButton")
        self._cancel_btn.setMinimumHeight(48)
        self._cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_btn.setVisible(False)
        self._cancel_btn.clicked.connect(self._on_cancel_generation)
        action_row.addWidget(self._cancel_btn)

        step2_layout.addLayout(action_row)

        # Progress and Live Log
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        step2_layout.addWidget(self._progress_bar)

        self._status_label = QLabel()
        self._status_label.setObjectName("secondaryText")
        step2_layout.addWidget(self._status_label)

        self._log_edit = QTextEdit()
        self._log_edit.setObjectName("logConsole")
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(80)
        step2_layout.addWidget(self._log_edit)

        content_layout.addWidget(self._step2_card)

        # ─────────────────────────────────────────────────────────
        # Generated Outputs: a plain, flat vertical list -- like a normal
        # page, not a boxed/numbered wizard step. Each row's required/
        # missing items show as a hover tooltip; clicking still opens the
        # full editor (which is also where items get marked resolved).
        # ─────────────────────────────────────────────────────────
        results_header_row = QHBoxLayout()
        self._step3_hint_lbl = QLabel()
        self._step3_hint_lbl.setObjectName("secondaryText")
        results_header_row.addWidget(self._step3_hint_lbl)
        results_header_row.addStretch()

        self._regenerate_btn = QPushButton("🔄")
        self._regenerate_btn.setObjectName("iconBtn")
        self._regenerate_btn.setFixedSize(36, 36)
        self._regenerate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._regenerate_btn.setVisible(False)
        self._regenerate_btn.clicked.connect(self._on_start_generation)
        results_header_row.addWidget(self._regenerate_btn)
        content_layout.addLayout(results_header_row)

        self._results_container = QVBoxLayout()
        self._results_container.setSpacing(10)
        content_layout.addLayout(self._results_container)

        # Absorb any leftover vertical space here instead of letting Qt
        # stretch the result cards themselves to fill the scroll area.
        content_layout.addStretch(1)

        self._scroll.setWidget(self._content_widget)
        outer_layout.addWidget(self._scroll, stretch=1)

    def _make_doc_toggle_card(self, title_key: str, desc_key: str, icon: str) -> tuple[QFrame, QPushButton, QLabel]:
        container = QFrame()
        container.setObjectName("docToggleCard")
        v = QVBoxLayout(container)
        v.setContentsMargins(14, 14, 14, 14)
        v.setSpacing(8)

        btn = QPushButton()
        btn.setObjectName("docToggleBtn")
        btn.setCheckable(True)
        btn.setChecked(True)
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        v.addWidget(btn)

        desc_label = QLabel()
        desc_label.setObjectName("secondaryText")
        desc_label.setWordWrap(True)
        v.addWidget(desc_label)
        v.addStretch()

        return container, btn, desc_label

    def update_ui_state(self) -> None:
        """Update all text and labels across the workspace."""
        lang = i18n.get_language()
        dark = theme.is_dark()

        # Update Text
        self._back_btn.setText(i18n.t("back_to_home_btn"))
        if self._project:
            self._app_title_lbl.setText(f"📁  {self._project.name}")
            self._app_subtitle_lbl.setText(self._project.description or i18n.t("no_description"))
        else:
            self._app_title_lbl.setText(i18n.t("app_title"))
            self._app_subtitle_lbl.setText(i18n.t("app_subtitle"))
        self._lang_btn.setText(i18n.t("lang_toggle_btn"))
        self._theme_btn.setText(i18n.t("theme_to_light") if dark else i18n.t("theme_to_dark"))
        self._regenerate_btn.setToolTip(i18n.t("regenerate_tooltip"))
        self._goto_generate_btn.setText(i18n.t("goto_generate_btn"))
        self._goto_generate_btn.setToolTip(i18n.t("goto_generate_tooltip"))
        self._update_back_button()

        self._step1_title_lbl.setText(i18n.t("step1_title"))
        self._browse_btn.setText(f"📂  {i18n.t('select_file_btn')}")
        self._file_path_edit.setPlaceholderText(i18n.t("file_placeholder"))
        self._preview_edit.setPlaceholderText(i18n.t("preview_placeholder"))

        if not self._selected_file_path:
            self._extract_status_lbl.setText(i18n.t("extract_empty"))

        self._step2_title_lbl.setText(i18n.t("step2_title"))
        self._btn_approval.setText(f"📝  {i18n.t('doc_approval')}")
        self._desc_approval.setText(i18n.t("doc_approval_desc"))

        self._btn_action_plan.setText(f"📊  {i18n.t('doc_action_plan')}")
        self._desc_action_plan.setText(i18n.t("doc_action_plan_desc"))

        self._btn_press.setText(f"📰  {i18n.t('doc_press_release')}")
        self._desc_press.setText(i18n.t("doc_press_release_desc"))

        self._start_btn.setText(f"🚀  {i18n.t('start_generation_btn')}")
        self._cancel_btn.setText(f"■  {i18n.t('cancel_btn')}")

        if not self._latest_result:
            self._status_label.setText(f"⏳  {i18n.t('status_waiting')}")

        self._step3_hint_lbl.setText(f"💡  {i18n.t('click_to_view')}")

        # Re-render output cards if result exists
        if self._latest_result:
            self._render_result_cards(self._latest_result)

    def _toggle_language(self) -> None:
        curr = i18n.get_language()
        new_lang = i18n.LANG_EN if curr == i18n.LANG_JA else i18n.LANG_JA
        i18n.set_language(new_lang)
        self.update_ui_state()
        self.language_changed.emit()

    def _toggle_theme(self) -> None:
        curr = theme.get_theme()
        new_theme = theme.THEME_LIGHT if curr == theme.THEME_DARK else theme.THEME_DARK
        theme.set_theme(new_theme)
        self.update_ui_state()
        self.theme_changed.emit()

    def _set_setup_visible(self, visible: bool) -> None:
        """
        Switch between the two views inside a project:
          - Output view  (visible=False): the flat list of generated
            documents. The default landing view once output exists.
          - Generation view (visible=True): Step 1 (input) + Step 2 (select
            & generate). The "🚀 Generate" button in the top bar reaches
            this from the Output view; the back button returns to the
            Output view rather than Home while here (see _on_back_clicked).
        """
        self._setup_visible = visible
        self._step1_card.setVisible(visible)
        self._step2_card.setVisible(visible)
        # No need to offer "go to generation" while already there.
        self._goto_generate_btn.setVisible(not visible and self._latest_result is not None)
        self._update_back_button()

    def _update_back_button(self) -> None:
        if self._setup_visible and self._latest_result is not None:
            self._back_btn.setText(i18n.t("back_to_output_btn"))
            self._back_btn.setToolTip(i18n.t("back_to_output_tooltip"))
        else:
            self._back_btn.setText(i18n.t("back_to_home_btn"))
            self._back_btn.setToolTip(i18n.t("back_to_home_tooltip"))

    def _on_back_clicked(self) -> None:
        on_generation_view_with_output = self._setup_visible and self._latest_result is not None
        if on_generation_view_with_output:
            self._set_setup_visible(False)  # return to the Output view
        else:
            self.back_requested.emit()  # nothing to return to -- go Home

    def set_project(self, project: Project) -> None:
        """Enter this workspace scoped to one project, resetting session state."""
        self._project = project
        self._extracted_text = ""
        self._selected_file_path = None
        self._latest_result = load_state(project.state_path)
        if self._latest_result is None:
            # Fallback for projects generated before internal-state tracking
            # existed: they have real exported .docx/.xlsx files but no JSON
            # state. Read those files' real text back in and show them the
            # same way as any other output, instead of a blank setup page.
            legacy_files = project.get_generated_files()
            if legacy_files:
                documents = {}
                for file_path in legacy_files:
                    doc = build_legacy_document(file_path)
                    documents[doc.kind] = doc
                self._latest_result = RunResult(documents=documents)
        self._file_path_edit.setText("")
        self._preview_edit.setPlainText("")
        self._progress_bar.setValue(0)
        self._log_edit.clear()
        self._regenerate_btn.setVisible(self._latest_result is not None)
        while self._results_container.count():
            item = self._results_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.update_ui_state()

        input_path = project.get_input_file_path()
        if input_path:
            self._set_input_file(input_path)
        else:
            self._extract_status_lbl.setText(i18n.t("extract_empty"))

        # Land on the Output view when this project already has generated
        # output (update_ui_state() above already rendered its rows).
        self._set_setup_visible(self._latest_result is None)

    def _on_browse_file(self) -> None:
        start_dir = (
            str(self._project.input_dir)
            if self._project and self._project.input_dir.is_dir()
            else str(Path.home())
        )
        selected, _ = QFileDialog.getOpenFileName(
            self,
            i18n.t("select_file_btn"),
            start_dir,
            "PowerPoint (*.pptx);;All Files (*.*)",
        )
        if not selected:
            return

        src_path = Path(selected)
        if self._project:
            try:
                saved_path = ProjectManager.save_input_document(self._project, src_path)
            except Exception as exc:
                ModernAlertBox.critical(self, i18n.t("error_title"), str(exc))
                return
            self._set_input_file(saved_path)
            self.project_updated.emit(self._project)
        else:
            self._set_input_file(src_path)

    def _set_input_file(self, file_path: Path) -> None:
        self._selected_file_path = file_path
        self._file_path_edit.setText(file_path.name)
        self._extract_status_lbl.setText(f"⏳  {i18n.t('extracting_text')}")
        self._preview_edit.setPlainText("")

        self._extraction_worker = ExtractionWorker(file_path)
        self._extraction_worker.finished.connect(self._on_extraction_finished)
        self._extraction_worker.error.connect(self._on_extraction_error)
        self._extraction_worker.start()

    def _on_extraction_finished(self, text: str, summary: str) -> None:
        self._extracted_text = text
        self._extract_status_lbl.setText(f"✓  {i18n.t('extract_success', summary=summary)}")
        self._preview_edit.setPlainText(text)

    def _on_extraction_error(self, message: str) -> None:
        self._extracted_text = ""
        self._extract_status_lbl.setText(i18n.t("extract_error"))
        self._preview_edit.setPlainText("")
        ModernAlertBox.warning(self, i18n.t("error_title"), message)

    def _on_start_generation(self) -> None:
        if not self._selected_file_path or not self._extracted_text.strip():
            ModernAlertBox.warning(self, "入力エラー", i18n.t("input_required"))
            return

        selections = []
        if self._btn_approval.isChecked():
            selections.append(APPROVAL)
        if self._btn_action_plan.isChecked():
            selections.append(ACTION_PLAN)
        if self._btn_press.isChecked():
            selections.append(PRESS_RELEASE)

        if not selections:
            ModernAlertBox.warning(self, "選択エラー", i18n.t("select_at_least_one"))
            return

        self._start_btn.setEnabled(False)
        self._cancel_btn.setVisible(True)
        self._progress_bar.setValue(0)
        self._log_edit.clear()
        self._status_label.setText(f"⚡  {i18n.t('status_generating')}")

        # In-memory generation (missing items still persist to the project's
        # own DB so the checklist survives across sessions).
        self._worker = GenerationWorker(
            source_text=self._extracted_text,
            selections=selections,
            source_path=self._selected_file_path,
            db_path=self._project.db_path if self._project else None,
            state_path=self._project.state_path if self._project else None,
        )
        self._worker.progress.connect(self._on_generation_progress)
        self._worker.log.connect(self._on_generation_log)
        self._worker.finished.connect(self._on_generation_finished)
        self._worker.error.connect(self._on_generation_error)
        self._worker.start()

    def _on_cancel_generation(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait(1000)
            self._on_generation_error(i18n.t("generation_cancelled"))

    def _on_generation_progress(self, percent: int, message: str) -> None:
        self._progress_bar.setValue(percent)
        self._status_label.setText(f"⚡  {message}")

    def _on_generation_log(self, text: str) -> None:
        self._log_edit.append(text)

    def _on_generation_finished(self, result: RunResult) -> None:
        self._start_btn.setEnabled(True)
        self._cancel_btn.setVisible(False)
        self._progress_bar.setValue(100)
        self._latest_result = result
        self._status_label.setText(f"✓  {i18n.t('status_complete')}")
        self._regenerate_btn.setVisible(True)

        self._render_result_cards(result)
        self._set_setup_visible(False)  # switch to the output view now that it exists
        if self._project:
            self.project_updated.emit(self._project)

    def _on_generation_error(self, message: str) -> None:
        self._start_btn.setEnabled(True)
        self._cancel_btn.setVisible(False)
        self._progress_bar.setValue(0)
        self._status_label.setText(f"⚠  {i18n.t('status_error')}")
        ModernAlertBox.critical(self, i18n.t("error_title"), message)

    @staticmethod
    def _build_missing_tooltip(unresolved: list, max_items: int = 6) -> str:
        """
        A quick-glance hover summary, not a full listing. Table-style
        documents (e.g. the Action Plan) repeat the same field names once
        per row, so a 16-row table can have 90+ raw missing items -- listing
        every one would make the tooltip unreadably long. Dedupe by field
        name and cap the list; the full, resolvable, per-row list still
        lives in the click-to-open editor.
        """
        seen: list[str] = []
        for mi in unresolved:
            if mi.field not in seen:
                seen.append(mi.field)

        shown = seen[:max_items]
        items_html = "".join(f"<li>{field}</li>" for field in shown)
        tooltip_title = i18n.t("missing_items_tooltip_title")
        html = f"<b>{tooltip_title}</b><ul style='margin:4px 0 0 -18px;'>{items_html}</ul>"

        remaining_field_types = len(seen) - len(shown)
        if remaining_field_types > 0:
            html += f"<div style='margin-top:4px;'>{i18n.t('missing_items_tooltip_more', n=remaining_field_types)}</div>"
        return html

    def _render_result_cards(self, result: RunResult) -> None:
        """
        Render the output list as a plain vertical list of rows -- title on
        the left, status on the right -- like a normal page, not a grid of
        boxes. Every entry (whether freshly generated or reconstructed from
        an older exported file) opens the same in-app text editor; nothing
        here ever launches an external app.
        """
        while self._results_container.count():
            item = self._results_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        lang = i18n.get_language()
        icons = {
            APPROVAL: "📝",
            ACTION_PLAN: "📊",
            PRESS_RELEASE: "📰",
        }

        for kind, doc in result.documents.items():
            row = ClickableCard()
            row.setObjectName("resultCard")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(18, 14, 18, 14)
            row_layout.setSpacing(14)

            doc_title = doc.display_name_ja if lang == i18n.LANG_JA else doc.display_name_en
            title_lbl = QLabel(f"{icons.get(kind, '📄')}  {doc_title}")
            title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            row_layout.addWidget(title_lbl, stretch=1)

            unresolved = [mi for mi in doc.missing_items if not mi.resolved]
            if unresolved:
                badge = QLabel(f"⚠ 要確認 {len(unresolved)}件" if lang == "ja" else f"⚠ Pending {len(unresolved)}")
                badge.setObjectName("badgeWarning")
                row.setToolTip(self._build_missing_tooltip(unresolved))
            else:
                badge = QLabel("✓ 生成完了" if lang == "ja" else "✓ Generated")
                badge.setObjectName("badgeSuccess")
                row.setToolTip("")
            row_layout.addWidget(badge)

            chevron = QLabel("›")
            chevron.setObjectName("mutedText")
            chevron.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            row_layout.addWidget(chevron)

            # The whole row opens the editor screen -- not just a sub-button.
            row.clicked.connect(lambda d=doc: self._open_preview_modal(d))

            self._results_container.addWidget(row)

    def _open_preview_modal(self, doc: GeneratedDocument) -> None:
        """Open the document editor screen for this document."""
        default_dir = self._project.output_dir if self._project else None
        db_path = self._project.db_path if self._project else None
        modal = DocumentPreviewModal(doc, parent=self, default_dir=default_dir, db_path=db_path)
        modal.exec()
        # Refresh cards in case the user edited/saved inside the editor
        # (e.g. a changed missing-item count, or items marked resolved).
        if self._latest_result:
            self._render_result_cards(self._latest_result)
            if self._project:
                save_state(self._project.state_path, self._latest_result, self._latest_result.selections)
        if self._project:
            self.project_updated.emit(self._project)

