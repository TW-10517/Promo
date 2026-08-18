"""
Entry point for the Dospara Promotion Document Generator.

Generates an Approval Document, an Action Plan, and a Press
Release from a single Planning Document (.pptx) using Claude / Ollama.

Run from source:
    python main.py
"""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from core import config
from ui.main_window import MainWindow
from ui.theme import THEME_DARK, build_palette, build_stylesheet


def main() -> int:
    config.load_env()

    # Set AppUserModelID so Windows Taskbar shows the custom QIcon instead of Python logo
    import ctypes
    try:
        myappid = 'dospara.promo.generator.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except AttributeError:
        pass  # Not on Windows

    app = QApplication(sys.argv)
    app.setApplicationName("Dospara Promotion Document Generator")

    # Set dark palette base and stylesheet
    app.setPalette(build_palette(THEME_DARK))
    app.setStyleSheet(build_stylesheet(THEME_DARK))

    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    try:
        config.get_api_key()
    except config.ConfigError as exc:
        QMessageBox.warning(window, "APIキー未設定", str(exc))

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
