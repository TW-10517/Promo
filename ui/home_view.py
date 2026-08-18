"""
Home / Landing screen: KPI hero header, searchable project card list, and
project creation dialog. Uses the same objectName-driven QSS as the rest of
the app (see ui/theme.py) so it renders correctly in both Dark and Light
mode, and the same ui/i18n.py strings so it follows the JA/EN toggle.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.project_manager import Project, ProjectManager
from ui import i18n, theme
from ui.alerts import ModernAlertBox
from PyQt6.QtGui import QPixmap
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════
# Create Project Dialog
# ═══════════════════════════════════════════════════════════════════

class CreateProjectDialog(QDialog):
    """Modal dialog for creating a new project."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._project: Project | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        self._container = QFrame()
        self._container.setObjectName("sectionCard")
        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        outer_layout.addWidget(self._container)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        title_label = QLabel(i18n.t("create_project_heading"))
        title_label.setObjectName("sectionHeading")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        desc_label = QLabel(i18n.t("create_project_desc"))
        desc_label.setObjectName("secondaryText")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        layout.addLayout(header_layout)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setFixedHeight(1)
        layout.addWidget(div)

        name_group = QVBoxLayout()
        name_group.setSpacing(8)
        name_label = QLabel(i18n.t("project_name_label") + " *")
        name_label.setObjectName("sectionHeading")
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText(i18n.t("project_name_placeholder"))
        self._name_edit.setMinimumHeight(42)
        name_group.addWidget(name_label)
        name_group.addWidget(self._name_edit)
        layout.addLayout(name_group)

        desc_group = QVBoxLayout()
        desc_group.setSpacing(8)
        desc_title = QLabel(i18n.t("project_desc_label"))
        desc_title.setObjectName("sectionHeading")
        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText(i18n.t("project_desc_placeholder"))
        self._desc_edit.setMinimumHeight(90)
        self._desc_edit.setMaximumHeight(120)
        desc_group.addWidget(desc_title)
        desc_group.addWidget(self._desc_edit)
        layout.addLayout(desc_group)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        self._cancel_btn = QPushButton(i18n.t("cancel_generic_btn"))
        self._cancel_btn.setObjectName("toolBtn")
        self._cancel_btn.setMinimumHeight(42)
        self._cancel_btn.setMinimumWidth(120)
        self._cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn)

        self._create_btn = QPushButton(i18n.t("create_project_submit_btn"))
        self._create_btn.setObjectName("primaryButton")
        self._create_btn.setMinimumHeight(42)
        self._create_btn.setMinimumWidth(160)
        self._create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._create_btn.clicked.connect(self._on_accept)
        btn_layout.addWidget(self._create_btn)

        layout.addLayout(btn_layout)

        # Focus the name field immediately so typing works without an extra click.
        self._name_edit.setFocus()

    def _on_accept(self) -> None:
        name = self._name_edit.text().strip()
        if not name:
            ModernAlertBox.warning(self, i18n.t("input_error_title"), i18n.t("project_name_required"))
            self._name_edit.setFocus()
            return

        desc = self._desc_edit.toPlainText().strip()
        try:
            self._project = ProjectManager.create_project(name=name, description=desc)
            self.accept()
        except Exception as exc:
            ModernAlertBox.critical(self, i18n.t("error_title"), f"{i18n.t('project_create_failed')}\n{exc}")

    def get_created_project(self) -> Project | None:
        return self._project


# ═══════════════════════════════════════════════════════════════════
# Project Card
# ═══════════════════════════════════════════════════════════════════

class ProjectCardWidget(QFrame):
    """Elevated card representing a single project."""

    open_requested = pyqtSignal(Project)
    delete_requested = pyqtSignal(Project)

    def __init__(self, project: Project, summary: dict, parent=None) -> None:
        super().__init__(parent)
        self.project = project
        self.summary = summary
        self.setObjectName("projectCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build_ui()

    def _build_ui(self) -> None:
        lang = i18n.get_language()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        gen_count = self.summary.get("generated_count", 0)
        accent_bar = QFrame()
        accent_bar.setFixedWidth(5)
        if gen_count == 3:
            accent_bar.setObjectName("accentBarSuccess")
        elif gen_count > 0:
            accent_bar.setObjectName("accentBarPrimary")
        else:
            accent_bar.setObjectName("accentBarNeutral")
        layout.addWidget(accent_bar)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 18, 20, 18)
        content_layout.setSpacing(12)

        top_layout = QHBoxLayout()
        name_label = QLabel(self.project.name)
        name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        top_layout.addWidget(name_label)
        top_layout.addStretch()

        if gen_count == 3:
            badge = QLabel("✓  " + i18n.t("docs_generated_badge", n=3))
            badge.setObjectName("badgeSuccess")
        elif gen_count > 0:
            badge = QLabel("◉  " + i18n.t("docs_generating_badge", n=gen_count))
            badge.setObjectName("badgePrimary")
        else:
            badge = QLabel("○  " + i18n.t("not_generated_badge"))
            badge.setObjectName("badgeNeutral")
        top_layout.addWidget(badge)
        content_layout.addLayout(top_layout)

        desc_text = self.project.description if self.project.description else i18n.t("no_description")
        desc_label = QLabel(desc_text)
        desc_label.setObjectName("secondaryText")
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(40)
        content_layout.addWidget(desc_label)

        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)

        has_input = self.summary.get("has_input", False)
        input_name = self.summary.get("input_name", "")
        if has_input and input_name:
            input_text = f"{i18n.t('input_pptx_label')}: {input_name}"
        else:
            input_text = f"{i18n.t('input_pptx_label')}: {i18n.t('input_pptx_unset')}"
        lbl_input = QLabel(input_text)
        lbl_input.setObjectName("secondaryText")
        info_layout.addWidget(lbl_input)

        pending = self.summary.get("pending_missing", 0)
        if pending > 0:
            lbl_missing = QLabel(i18n.t("pending_confirm_badge", n=pending))
            lbl_missing.setObjectName("badgeWarning")
        elif gen_count > 0:
            lbl_missing = QLabel(i18n.t("no_missing_badge"))
            lbl_missing.setObjectName("badgeSuccess")
        else:
            lbl_missing = QLabel(i18n.t("missing_dash"))
            lbl_missing.setObjectName("mutedText")
        info_layout.addWidget(lbl_missing)

        info_layout.addStretch()

        created_str = self.project.created_at[:10] if self.project.created_at else ""
        lbl_date = QLabel(i18n.t("created_at_label", date=created_str))
        lbl_date.setObjectName("mutedText")
        info_layout.addWidget(lbl_date)

        content_layout.addLayout(info_layout)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        del_btn = QPushButton("🗑")
        del_btn.setObjectName("iconBtnDanger")
        del_btn.setFixedSize(38, 38)
        del_btn.setToolTip(i18n.t("delete_tooltip"))
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.project))
        action_layout.addWidget(del_btn)

        action_layout.addStretch()

        open_btn = QPushButton(i18n.t("open_project_btn"))
        open_btn.setObjectName("primaryButton")
        open_btn.setMinimumWidth(120)
        open_btn.setMinimumHeight(38)
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.clicked.connect(lambda: self.open_requested.emit(self.project))
        action_layout.addWidget(open_btn)

        content_layout.addLayout(action_layout)
        layout.addLayout(content_layout)

    def enterEvent(self, event) -> None:  # noqa: N802
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(99, 102, 241, 40))
        self.setGraphicsEffect(shadow)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self.setGraphicsEffect(None)
        super().leaveEvent(event)


# ═══════════════════════════════════════════════════════════════════
# Home View
# ═══════════════════════════════════════════════════════════════════

class ProjectHomeView(QWidget):
    """Home / Landing Screen: hero KPIs, search, and project card list."""

    project_selected = pyqtSignal(Project)
    theme_changed = pyqtSignal()
    language_changed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._projects: list[Project] = []
        self._build_ui()
        self.update_ui_state()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(20)

        # ── Hero Header ──
        self._hero_frame = QFrame()
        self._hero_frame.setObjectName("heroBanner")
        hero_layout = QHBoxLayout(self._hero_frame)
        hero_layout.setContentsMargins(32, 26, 32, 26)
        hero_layout.setSpacing(24)

        logo_path = Path(__file__).parent.parent / "assets" / "logo.jpg"
        if logo_path.exists():
            from PyQt6.QtGui import QPixmap
            logo_lbl = QLabel()
            pixmap = QPixmap(str(logo_path)).scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pixmap)
            hero_layout.addWidget(logo_lbl)

        title_group = QVBoxLayout()
        title_group.setSpacing(6)
        self._title_lbl = QLabel()
        self._title_lbl.setObjectName("heroTitle")
        self._title_lbl.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        title_group.addWidget(self._title_lbl)

        self._subtitle_lbl = QLabel()
        self._subtitle_lbl.setObjectName("heroSubtitle")
        self._subtitle_lbl.setWordWrap(True)
        title_group.addWidget(self._subtitle_lbl)
        hero_layout.addLayout(title_group, stretch=1)

        # Right: theme/lang toggles + AI badge + KPI chips
        controls_group = QVBoxLayout()
        controls_group.setSpacing(10)

        top_controls = QHBoxLayout()
        top_controls.setSpacing(8)
        top_controls.addStretch()

        self._theme_btn = QPushButton()
        self._theme_btn.setObjectName("toolBtn")
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self._toggle_theme)
        top_controls.addWidget(self._theme_btn)

        self._lang_btn = QPushButton()
        self._lang_btn.setObjectName("toolBtn")
        self._lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._lang_btn.clicked.connect(self._toggle_language)
        top_controls.addWidget(self._lang_btn)

        controls_group.addLayout(top_controls)

        kpi_container = QHBoxLayout()
        kpi_container.setSpacing(12)
        self._kpi_projects = self._make_kpi_chip("0", "kpiValuePrimary")
        kpi_container.addWidget(self._kpi_projects)
        self._kpi_docs = self._make_kpi_chip("0", "kpiValueSuccess")
        kpi_container.addWidget(self._kpi_docs)
        self._kpi_missing = self._make_kpi_chip("0", "kpiValueWarning")
        kpi_container.addWidget(self._kpi_missing)
        controls_group.addLayout(kpi_container)

        hero_layout.addLayout(controls_group)

        main_layout.addWidget(self._hero_frame)

        # ── Search & Toolbar ──
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        self._search_edit = QLineEdit()
        self._search_edit.setObjectName("searchBar")
        self._search_edit.setMinimumHeight(44)
        self._search_edit.textChanged.connect(self._filter_projects)
        toolbar.addWidget(self._search_edit, stretch=1)

        self._create_btn = QPushButton()
        self._create_btn.setObjectName("primaryButton")
        self._create_btn.setMinimumHeight(44)
        self._create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._create_btn.clicked.connect(self._open_create_dialog)
        toolbar.addWidget(self._create_btn)

        main_layout.addLayout(toolbar)

        # ── Project Cards Scroll Area ──
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 8, 0)
        self._cards_layout.setSpacing(12)
        self._cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._scroll.setWidget(self._cards_container)
        main_layout.addWidget(self._scroll, stretch=1)

    @staticmethod
    def _make_kpi_chip(value: str, accent_color: str) -> QFrame:
        chip = QFrame()
        chip.setObjectName("kpiChip")
        chip_layout = QVBoxLayout(chip)
        chip_layout.setContentsMargins(16, 8, 16, 8)
        chip_layout.setSpacing(2)
        chip_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        val_lbl = QLabel(value)
        val_lbl.setObjectName(accent_color)
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip_layout.addWidget(val_lbl)

        name_lbl = QLabel()
        name_lbl.setObjectName("kpiLabel")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip_layout.addWidget(name_lbl)

        return chip

    # ── i18n / theme ──

    def update_ui_state(self) -> None:
        """Re-apply all text and rebuild the card list under the current theme."""
        self._title_lbl.setText("✦  " + i18n.t("app_title"))
        self._subtitle_lbl.setText(i18n.t("home_subtitle"))
        dark = theme.is_dark()
        self._theme_btn.setText(i18n.t("theme_to_light") if dark else i18n.t("theme_to_dark"))
        self._lang_btn.setText(i18n.t("lang_toggle_btn"))
        self._search_edit.setPlaceholderText(i18n.t("search_placeholder"))
        self._create_btn.setText(i18n.t("create_project_btn"))

        self._kpi_projects.findChild(QLabel, "kpiLabel").setText(i18n.t("kpi_projects"))
        self._kpi_docs.findChild(QLabel, "kpiLabel").setText(i18n.t("kpi_docs"))
        self._kpi_missing.findChild(QLabel, "kpiLabel").setText(i18n.t("kpi_missing"))

        self.refresh()

    def _toggle_theme(self) -> None:
        new_theme = theme.THEME_LIGHT if theme.get_theme() == theme.THEME_DARK else theme.THEME_DARK
        theme.set_theme(new_theme)
        self.update_ui_state()
        self.theme_changed.emit()

    def _toggle_language(self) -> None:
        new_lang = i18n.LANG_EN if i18n.get_language() == i18n.LANG_JA else i18n.LANG_JA
        i18n.set_language(new_lang)
        self.update_ui_state()
        self.language_changed.emit()

    # ── Data ──

    def refresh(self) -> None:
        """Reload project list and recalculate KPI statistics."""
        self._projects = ProjectManager.list_projects()
        self._update_kpi_stats()
        self._filter_projects()

    def _update_kpi_stats(self) -> None:
        total_projects = len(self._projects)
        total_docs = 0
        total_missing = 0
        for p in self._projects:
            s = ProjectManager.get_project_status_summary(p.id)
            total_docs += s.get("generated_count", 0)
            total_missing += s.get("pending_missing", 0)

        self._kpi_projects.findChild(QLabel, "kpiValuePrimary").setText(str(total_projects))
        self._kpi_docs.findChild(QLabel, "kpiValueSuccess").setText(str(total_docs))
        self._kpi_missing.findChild(QLabel, "kpiValueWarning").setText(str(total_missing))

    def _filter_projects(self) -> None:
        query = self._search_edit.text().strip().lower()

        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = [
            p for p in self._projects
            if not query or query in p.name.lower() or query in p.description.lower()
        ]

        if not filtered:
            empty_box = QFrame()
            empty_box.setObjectName("emptyState")
            empty_layout = QVBoxLayout(empty_box)
            empty_layout.setContentsMargins(48, 48, 48, 48)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.setSpacing(14)

            icon_lbl = QLabel("📋")
            icon_lbl.setFont(QFont("Segoe UI Emoji", 36))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(icon_lbl)

            msg_title = QLabel(
                i18n.t("no_projects_title") if not self._projects else i18n.t("no_projects_filtered_title")
            )
            msg_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            msg_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(msg_title)

            msg_sub = QLabel(i18n.t("no_projects_sub"))
            msg_sub.setObjectName("secondaryText")
            msg_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(msg_sub)

            btn = QPushButton(i18n.t("create_project_btn"))
            btn.setObjectName("primaryButton")
            btn.setMinimumHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(self._open_create_dialog)
            empty_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

            self._cards_layout.addWidget(empty_box)
            return

        for p in filtered:
            summary = ProjectManager.get_project_status_summary(p.id)
            card = ProjectCardWidget(p, summary)
            card.open_requested.connect(self.project_selected.emit)
            card.delete_requested.connect(self._on_delete_project)
            self._cards_layout.addWidget(card)

    def _open_create_dialog(self) -> None:
        dlg = CreateProjectDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_proj = dlg.get_created_project()
            if new_proj:
                self.refresh()
                self.project_selected.emit(new_proj)

    def _on_delete_project(self, project: Project) -> None:
        ans = ModernAlertBox.question(
            self,
            i18n.t("delete_confirm_title"),
            i18n.t("delete_confirm_msg", name=project.name),
        )
        if ans:
            ProjectManager.delete_project(project.id)
            self.refresh()
