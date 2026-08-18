"""
Main application window: switches between the Home screen (project list)
and the project-scoped generation Workspace.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
)

from core.project_manager import Project
from ui import i18n
from ui.alerts import ModernAlertBox
from ui.home_view import ProjectHomeView
from ui.workspace_view import PromotionGenWorkspace


class MainWindow(QMainWindow):
    """The main window hosting the Home screen and the project Workspace."""

    def __init__(self) -> None:
        super().__init__()
        self.resize(1080, 880)
        self.setMinimumSize(960, 740)

        # Set the application logo
        logo_path = Path(__file__).parent.parent / "assets" / "logo.jpg"
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

        self._stacked = QStackedWidget()
        self.setCentralWidget(self._stacked)

        # Page 0: Home screen (project list)
        self._home_view = ProjectHomeView()
        self._home_view.project_selected.connect(self._open_project_workspace)
        self._home_view.theme_changed.connect(self._on_theme_or_lang_changed)
        self._home_view.language_changed.connect(self._on_theme_or_lang_changed)
        self._stacked.addWidget(self._home_view)

        # Page 1: Project workspace (generate / preview / export)
        self._workspace = PromotionGenWorkspace()
        self._workspace.back_requested.connect(self._back_to_home)
        self._workspace.project_updated.connect(lambda _proj: self._home_view.refresh())
        self._workspace.theme_changed.connect(self._on_theme_or_lang_changed)
        self._workspace.language_changed.connect(self._on_theme_or_lang_changed)
        self._stacked.addWidget(self._workspace)

        self._stacked.setCurrentIndex(0)
        self._update_title()

    def _open_project_workspace(self, project: Project) -> None:
        """Switch to the workspace, scoped to the given project."""
        self._workspace.set_project(project)
        self._stacked.setCurrentIndex(1)
        self._update_title(project)

    def _back_to_home(self) -> None:
        """Switch back to the home screen."""
        self._home_view.refresh()
        self._stacked.setCurrentIndex(0)
        self._update_title()

    def _on_theme_or_lang_changed(self) -> None:
        """Theme/language are global state -- keep whichever screen isn't
        currently visible in sync too, so switching back to it looks right."""
        self._home_view.update_ui_state()
        self._workspace.update_ui_state()
        self._update_title()

    def _update_title(self, project: Project | None = None) -> None:
        base = i18n.t("app_title")
        self.setWindowTitle(f"{base} — {project.name}" if project else base)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Ask before closing if a generation job is running in the workspace."""
        if hasattr(self, "_workspace") and getattr(self._workspace, "_worker", None) and self._workspace._worker.isRunning():
            answer = ModernAlertBox.question(
                self,
                i18n.t("warning_title"),
                i18n.t("generation_in_progress_exit"),
            )
            if not answer:
                event.ignore()
                return
            self._workspace._worker.terminate()
            self._workspace._worker.wait(3000)
        event.accept()
