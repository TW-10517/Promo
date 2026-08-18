"""Modern, premium alert boxes to replace standard QMessageBox."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame

from ui import i18n


class ModernAlertBox(QDialog):
    """A frameless, rounded dialog that respects the global app theme."""
    
    def __init__(self, title: str, message: str, is_error: bool = False, is_question: bool = False, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._is_question = is_question

        self._build_ui(title, message, is_error)

    def _build_ui(self, title: str, message: str, is_error: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # The main card container acts as the visible dialog
        self._container = QFrame()
        self._container.setObjectName("sectionCardAccent" if is_error else "sectionCard")
        
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        icon_lbl = QLabel()
        if is_error:
            icon_lbl.setText("❌")
        elif self._is_question:
            icon_lbl.setText("❓")
        else:
            icon_lbl.setText("ℹ️")
            
        from PyQt6.QtGui import QFont
        font = QFont()
        font.setPointSize(20)
        icon_lbl.setFont(font)
        header_layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("sectionHeading")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        container_layout.addLayout(header_layout)

        # Message
        msg_lbl = QLabel(message)
        msg_lbl.setObjectName("secondaryText")
        msg_lbl.setWordWrap(True)
        container_layout.addWidget(msg_lbl)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        if self._is_question:
            cancel_btn = QPushButton("キャンセル" if i18n.get_language() == "ja" else "Cancel")
            cancel_btn.setObjectName("toolBtn")
            cancel_btn.setMinimumHeight(38)
            cancel_btn.setMinimumWidth(100)
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.clicked.connect(self.reject)
            btn_layout.addWidget(cancel_btn)

            ok_btn = QPushButton("はい" if i18n.get_language() == "ja" else "Yes")
            ok_btn.setObjectName("dangerButton" if is_error else "primaryButton")
            ok_btn.setMinimumHeight(38)
            ok_btn.setMinimumWidth(100)
            ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            ok_btn.clicked.connect(self.accept)
            btn_layout.addWidget(ok_btn)
        else:
            ok_btn = QPushButton("OK")
            ok_btn.setObjectName("primaryButton")
            ok_btn.setMinimumHeight(38)
            ok_btn.setMinimumWidth(100)
            ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            ok_btn.clicked.connect(self.accept)
            btn_layout.addWidget(ok_btn)

        container_layout.addLayout(btn_layout)
        layout.addWidget(self._container)

    @classmethod
    def warning(cls, parent, title: str, message: str) -> None:
        dlg = cls(title, message, is_error=True, parent=parent)
        dlg.exec()

    @classmethod
    def critical(cls, parent, title: str, message: str) -> None:
        dlg = cls(title, message, is_error=True, parent=parent)
        dlg.exec()

    @classmethod
    def information(cls, parent, title: str, message: str) -> None:
        dlg = cls(title, message, is_error=False, parent=parent)
        dlg.exec()

    @classmethod
    def question(cls, parent, title: str, message: str) -> bool:
        dlg = cls(title, message, is_error=False, is_question=True, parent=parent)
        return dlg.exec() == QDialog.DialogCode.Accepted
