"""
Dual-Theme (Dark / Light) System for Dospara Promotion Document Generator.

Architecture:
- Clean class & object-name based stylesheet generation.
- No conflicting inline styles.
- Flawless contrast in BOTH Dark Mode and Light Mode.
"""

from __future__ import annotations

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

FONT_FAMILY = '"Segoe UI", "Meiryo UI", "Yu Gothic UI", "Noto Sans JP", -apple-system, BlinkMacSystemFont, sans-serif'
CODE_FONT = '"Cascadia Code", "Consolas", "Courier New", monospace'

THEME_DARK = "dark"
THEME_LIGHT = "light"

CURRENT_THEME = THEME_DARK


def is_dark() -> bool:
    return CURRENT_THEME == THEME_DARK


def build_palette(theme_name: str) -> QPalette:
    dark = (theme_name == THEME_DARK)
    palette = QPalette()

    bg = QColor("#0B0F19" if dark else "#F8FAFC")
    bg_elevated = QColor("#111827" if dark else "#FFFFFF")
    card_bg = QColor("#131B2E" if dark else "#FFFFFF")
    text_primary = QColor("#F1F5F9" if dark else "#0F172A")
    text_sec = QColor("#94A3B8" if dark else "#475569")
    accent = QColor("#6366F1")

    palette.setColor(QPalette.ColorRole.Window, bg)
    palette.setColor(QPalette.ColorRole.WindowText, text_primary)
    palette.setColor(QPalette.ColorRole.Base, bg_elevated)
    palette.setColor(QPalette.ColorRole.AlternateBase, card_bg)
    palette.setColor(QPalette.ColorRole.ToolTipBase, bg_elevated)
    palette.setColor(QPalette.ColorRole.ToolTipText, text_primary)
    palette.setColor(QPalette.ColorRole.Text, text_primary)
    palette.setColor(QPalette.ColorRole.Button, card_bg)
    palette.setColor(QPalette.ColorRole.ButtonText, text_primary)
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    return palette


def build_stylesheet(theme_name: str) -> str:
    dark = (theme_name == THEME_DARK)

    # Base Colors
    bg = "#0B0F19" if dark else "#F1F5F9"
    surface = "#111827" if dark else "#FFFFFF"
    card_bg = "#131B2E" if dark else "#FFFFFF"
    card_hover = "#1A2540" if dark else "#F8FAFC"
    subcard_bg = "#0F172A" if dark else "#F8FAFC"

    border = "#1E293B" if dark else "#CBD5E1"
    border_subtle = "#162032" if dark else "#E2E8F0"
    border_focus = "#818CF8" if dark else "#4F46E5"

    text_primary = "#F1F5F9" if dark else "#0F172A"
    text_secondary = "#94A3B8" if dark else "#334155"
    text_muted = "#64748B" if dark else "#64748B"

    primary = "#818CF8" if dark else "#4F46E5"
    primary_hover = "#6366F1" if dark else "#4338CA"
    primary_light = "#1E1B4B" if dark else "#EEF2FF"

    console_bg = "#0D1117" if dark else "#F8FAFC"
    console_text = "#38BDF8" if dark else "#0369A1"

    scroll_handle = "#334155" if dark else "#94A3B8"
    scroll_handle_hover = "#475569" if dark else "#64748B"

    badge_success_bg = "#052E16" if dark else "#DCFCE7"
    badge_success_text = "#34D399" if dark else "#15803D"
    badge_success_border = "#065F46" if dark else "#86EFAC"

    badge_warning_bg = "#451A03" if dark else "#FEF3C7"
    badge_warning_text = "#FBBF24" if dark else "#B45309"
    badge_warning_border = "#78350F" if dark else "#FCD34D"

    badge_primary_bg = "#1E1B4B" if dark else "#EEF2FF"
    badge_primary_text = "#818CF8" if dark else "#4338CA"
    badge_primary_border = "#312E81" if dark else "#A5B4FC"

    badge_neutral_bg = "#1E293B" if dark else "#F1F5F9"
    badge_neutral_text = text_muted
    badge_neutral_border = border

    kpi_chip_bg = "rgba(255, 255, 255, 15)"
    kpi_chip_border = "rgba(255, 255, 255, 30)"

    return f"""
/* ─── Global Reset & Base Typography ────────────────────────── */
* {{
    font-family: {FONT_FAMILY};
    color: {text_primary};
    font-size: 14px;
    outline: none;
}}

QWidget {{
    background-color: {bg};
    color: {text_primary};
}}

QMainWindow, QDialog {{
    background-color: {bg};
}}

/* ─── Scroll Area ───────────────────────────────────────────── */
QScrollArea {{
    background-color: {bg};
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background-color: {bg};
}}

QScrollBar:vertical {{
    border: none;
    background: {bg};
    width: 6px;
    border-radius: 3px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {scroll_handle};
    min-height: 30px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{
    background: {scroll_handle_hover};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::horizontal {{
    border: none;
    background: {bg};
    height: 6px;
    border-radius: 3px;
    margin: 2px 4px;
}}
QScrollBar::handle:horizontal {{
    background: {scroll_handle};
    min-width: 30px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {scroll_handle_hover};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QScrollBar::add-page, QScrollBar::sub-page {{
    background: {bg};
}}

/* ─── Top Header Bar ────────────────────────────────────────── */
QFrame#topBar {{
    background-color: {card_bg};
    border: 1px solid {border};
    border-radius: 14px;
}}
QFrame#topBar QLabel {{
    background-color: transparent;
    color: {text_primary};
    border: none;
}}
QLabel#appTitle {{
    font-size: 16px;
    font-weight: bold;
    color: {text_primary};
    background-color: transparent;
}}
QLabel#appSubtitle {{
    font-size: 12px;
    color: {text_secondary};
    background-color: transparent;
}}

/* ─── Section Cards ─────────────────────────────────────────── */
QFrame#sectionCard {{
    background-color: {card_bg};
    border: 1px solid {border};
    border-radius: 14px;
}}
QFrame#sectionCard QLabel {{
    background-color: transparent;
    color: {text_primary};
    border: none;
}}

QFrame#sectionCardAccent {{
    background-color: {card_bg};
    border: 1px solid {border};
    border-radius: 14px;
    border-top: 3.5px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:0.5 #7C3AED, stop:1 #8B5CF6);
}}
QFrame#sectionCardAccent QLabel {{
    background-color: transparent;
    color: {text_primary};
    border: none;
}}

QLabel#sectionHeading {{
    font-size: 14px;
    font-weight: 700;
    color: {primary};
    background-color: transparent;
}}

QLabel#secondaryText {{
    font-size: 12px;
    color: {text_secondary};
    background-color: transparent;
}}

QLabel#mutedText {{
    font-size: 12px;
    color: {text_muted};
    background-color: transparent;
}}

/* ─── Sub Cards (e.g. Document Toggle Cards) ─────────────────── */
QFrame#docToggleCard {{
    background-color: {subcard_bg};
    border: 1px solid {border_subtle};
    border-radius: 12px;
}}
QFrame#docToggleCard QLabel {{
    background-color: transparent;
    color: {text_secondary};
    border: none;
    font-size: 12px;
}}

QFrame#resultCard {{
    background-color: {card_bg};
    border: 1.5px solid {primary};
    border-radius: 12px;
}}
QFrame#resultCard:hover {{
    background-color: {card_hover};
    border-color: {primary_hover};
}}
QFrame#resultCard QLabel {{
    background-color: transparent;
    color: {text_primary};
    border: none;
}}

/* ─── Missing Items List (inside the document editor modal) ──── */
QListWidget#missingItemsList {{
    background-color: {subcard_bg};
    border: 1px solid {border_subtle};
    border-radius: 10px;
    padding: 4px;
    outline: none;
}}
QListWidget#missingItemsList::item {{
    padding: 8px 10px;
    border-radius: 8px;
    color: {text_primary};
}}
QListWidget#missingItemsList::item:hover {{
    background-color: {card_hover};
}}
QListWidget#missingItemsList::item:selected {{
    background-color: {primary_light};
    color: {primary};
}}

/* ─── Inputs & TextEdits ─────────────────────────────────────── */
QLineEdit {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    color: {text_primary};
    selection-background-color: {primary_light};
    selection-color: {primary};
}}
QLineEdit:focus {{
    border: 1.5px solid {border_focus};
}}
QLineEdit[readOnly="true"] {{
    background-color: {subcard_bg};
    color: {text_secondary};
}}

QTextEdit#logConsole {{
    background-color: {console_bg};
    color: {console_text};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 12px 16px;
    font-family: {CODE_FONT};
    font-size: 13px;
    line-height: 1.5;
    selection-background-color: {primary_light};
    selection-color: {primary};
}}

/* ─── Buttons ────────────────────────────────────────────────── */
QPushButton {{
    font-weight: 600;
    border-radius: 10px;
    padding: 9px 18px;
    font-size: 14px;
    border: 1px solid {border};
    background-color: {card_bg};
    color: {text_primary};
}}
QPushButton:hover {{
    background-color: {primary_light};
    border-color: {primary};
    color: {primary};
}}
QPushButton:pressed {{
    background-color: {border};
}}

/* Header Toolbar Buttons */
QPushButton#toolBtn {{
    background-color: {subcard_bg};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
    color: {text_primary};
}}
QPushButton#toolBtn:hover {{
    background-color: {primary_light};
    border-color: {primary};
    color: {primary};
}}

/* Icon-only buttons: a shape/glyph alone, with a hover tooltip for meaning */
QPushButton#iconBtn {{
    background-color: {subcard_bg};
    border: 1px solid {border};
    border-radius: 9px;
    padding: 0px;
    font-size: 16px;
    color: {text_primary};
}}
QPushButton#iconBtn:hover {{
    background-color: {primary_light};
    border-color: {primary};
    color: {primary};
}}
QPushButton#iconBtn:pressed {{
    background-color: {border};
}}
QPushButton#iconBtnDanger {{
    background-color: {subcard_bg};
    border: 1px solid {border};
    border-radius: 9px;
    padding: 0px;
    font-size: 16px;
    color: {"#F87171" if dark else "#DC2626"};
}}
QPushButton#iconBtnDanger:hover {{
    background-color: {"#450A0A" if dark else "#FEE2E2"};
    border-color: {"#F87171" if dark else "#DC2626"};
}}
QPushButton#iconBtnPrimary {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:0.5 #7C3AED, stop:1 #8B5CF6);
    border: none;
    border-radius: 9px;
    padding: 0px;
    font-size: 16px;
    color: #FFFFFF;
}}
QPushButton#iconBtnPrimary:hover {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4F46E5, stop:0.5 #6D28D9, stop:1 #7C3AED);
}}

/* Primary Buttons */
QPushButton#primaryButton, QPushButton[primary="true"] {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:0.5 #7C3AED, stop:1 #8B5CF6);
    color: #FFFFFF;
    border: none;
    padding: 11px 22px;
    font-size: 14px;
    font-weight: 700;
    border-radius: 10px;
}}
QPushButton#primaryButton:hover, QPushButton[primary="true"]:hover {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4F46E5, stop:0.5 #6D28D9, stop:1 #7C3AED);
    color: #FFFFFF;
}}
QPushButton#primaryButton:pressed, QPushButton[primary="true"]:pressed {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4338CA, stop:0.5 #5B21B6, stop:1 #6D28D9);
    color: #FFFFFF;
}}

/* Danger Buttons */
QPushButton#dangerButton, QPushButton[danger="true"] {{
    background-color: {"#450A0A" if dark else "#FEE2E2"};
    color: {"#F87171" if dark else "#DC2626"};
    border: 1px solid {"#7F1D1D" if dark else "#FCA5A5"};
}}
QPushButton#dangerButton:hover, QPushButton[danger="true"]:hover {{
    background-color: {"#7F1D1D" if dark else "#FECACA"};
}}

/* Document Toggle Checkable Buttons */
QPushButton#docToggleBtn {{
    text-align: left;
    padding: 10px 14px;
    font-size: 14px;
    font-weight: 700;
    border: 1.5px dashed {border};
    border-radius: 10px;
    background-color: {surface};
    color: {text_secondary};
}}
QPushButton#docToggleBtn:hover {{
    border-color: {primary};
    border-style: solid;
    background-color: {primary_light};
    color: {primary};
}}
QPushButton#docToggleBtn:checked {{
    border: 2px solid {primary};
    border-style: solid;
    background-color: {primary_light};
    color: {primary};
}}

/* ─── Badges ─────────────────────────────────────────────────── */
QLabel#badgeSuccess {{
    background-color: {badge_success_bg};
    color: {badge_success_text};
    border: 1px solid {badge_success_border};
    border-radius: 12px;
    padding: 4px 12px;
    font-weight: 700;
    font-size: 11px;
}}

QLabel#badgeWarning {{
    background-color: {badge_warning_bg};
    color: {badge_warning_text};
    border: 1px solid {badge_warning_border};
    border-radius: 12px;
    padding: 4px 12px;
    font-weight: 700;
    font-size: 11px;
}}

QLabel#badgePrimary {{
    background-color: {badge_primary_bg};
    color: {badge_primary_text};
    border: 1px solid {badge_primary_border};
    border-radius: 12px;
    padding: 4px 12px;
    font-weight: 700;
    font-size: 11px;
}}

QLabel#badgeNeutral {{
    background-color: {badge_neutral_bg};
    color: {badge_neutral_text};
    border: 1px solid {badge_neutral_border};
    border-radius: 12px;
    padding: 4px 12px;
    font-weight: 700;
    font-size: 11px;
}}

/* ─── Home Screen: Hero Banner ───────────────────────────────── */
QFrame#heroBanner {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0F0A2E, stop:0.3 #1E1B4B, stop:0.6 #312E81, stop:1 #4338CA);
    border-radius: 18px;
    border: 1px solid #312E81;
}}
QFrame#heroBanner QLabel {{
    background-color: transparent;
    border: none;
}}
QLabel#heroTitle {{
    color: #FFFFFF;
    font-size: 17px;
    font-weight: bold;
}}
QLabel#heroSubtitle {{
    color: #C7C9F0;
    font-size: 13px;
}}
QFrame#kpiChip {{
    background-color: {kpi_chip_bg};
    border: 1px solid {kpi_chip_border};
    border-radius: 12px;
}}
QFrame#kpiChip QLabel {{
    background-color: transparent;
    border: none;
}}
QLabel#kpiValue {{
    font-size: 18px;
    font-weight: bold;
}}
QLabel#kpiLabel {{
    color: #C7C9F0;
    font-size: 11px;
    font-weight: 600;
}}

/* Pill-shaped search bar on the home screen */
QLineEdit#searchBar {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 22px;
    padding: 10px 20px;
    font-size: 14px;
    color: {text_primary};
}}
QLineEdit#searchBar:focus {{
    border: 1.5px solid {border_focus};
}}

/* ─── Home Screen: Project Cards ──────────────────────────────── */
QFrame#projectCard {{
    background-color: {card_bg};
    border: 1px solid {border};
    border-radius: 16px;
}}
QFrame#projectCard:hover {{
    border: 1.5px solid {primary};
    background-color: {card_hover};
}}
QFrame#projectCard QLabel {{
    background-color: transparent;
    border: none;
    color: {text_primary};
}}
QFrame#emptyState {{
    background-color: {card_bg};
    border: 2px dashed {border};
    border-radius: 18px;
}}
QFrame#emptyState QLabel {{
    background-color: transparent;
    border: none;
}}

/* ─── Progress Bar ───────────────────────────────────────────── */
QProgressBar {{
    border: none;
    border-radius: 8px;
    background-color: {border};
    text-align: center;
    font-weight: 700;
    font-size: 11px;
    color: {text_secondary};
    height: 14px;
}}
QProgressBar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:0.4 #8B5CF6, stop:0.8 #A78BFA, stop:1 #6366F1);
    border-radius: 8px;
}}

/* ─── Tables ─────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {card_bg};
    border: 1px solid {border};
    border-radius: 10px;
    gridline-color: {border_subtle};
    selection-background-color: {primary_light};
    selection-color: {text_primary};
    alternate-background-color: {subcard_bg};
    color: {text_primary};
}}
QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid {border_subtle};
    color: {text_primary};
}}
QTableWidget::item:hover {{
    background-color: {primary_light};
}}
QHeaderView {{
    background-color: {subcard_bg};
}}
QHeaderView::section {{
    background-color: {subcard_bg};
    color: {text_secondary};
    font-weight: 700;
    font-size: 12px;
    border: none;
    border-bottom: 1px solid {border};
    padding: 10px 12px;
}}

/* ─── Message Boxes ──────────────────────────────────────────── */
QMessageBox {{
    background-color: {surface};
}}
QMessageBox QLabel {{
    color: {text_primary};
}}

/* ─── Tooltips (hover hint text for icon-only buttons) ───────── */
QToolTip {{
    background-color: {"#1E293B" if dark else "#0F172A"};
    color: #F1F5F9;
    border: 1px solid {primary};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
}}

/* Editable "notepad" text view in the document editor screen */
QTextEdit#editorText {{
    background-color: {console_bg};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 16px 20px;
    font-family: {CODE_FONT};
    font-size: 13px;
    line-height: 1.6;
    selection-background-color: {primary_light};
    selection-color: {primary};
}}

/* ── KPI & Accent Bars ── */
QFrame#accentBarSuccess {{ background-color: #34D399; border-top-left-radius: 16px; border-bottom-left-radius: 16px; }}
QFrame#accentBarPrimary {{ background-color: #818CF8; border-top-left-radius: 16px; border-bottom-left-radius: 16px; }}
QFrame#accentBarNeutral {{ background-color: {border}; border-top-left-radius: 16px; border-bottom-left-radius: 16px; }}

QLabel#kpiValueSuccess {{ color: #A7F3D0; }}
QLabel#kpiValuePrimary {{ color: #C7D2FE; }}
QLabel#kpiValueWarning {{ color: #FDE68A; }}
QLabel#kpiValueNeutral {{ color: {text_muted}; }}
"""


def set_theme(theme_name: str) -> None:
    global CURRENT_THEME
    if theme_name in (THEME_DARK, THEME_LIGHT):
        CURRENT_THEME = theme_name
        app = QApplication.instance()
        if app:
            app.setPalette(build_palette(theme_name))
            app.setStyleSheet(build_stylesheet(theme_name))


def get_theme() -> str:
    return CURRENT_THEME


GLOBAL_STYLESHEET = build_stylesheet(THEME_DARK)
