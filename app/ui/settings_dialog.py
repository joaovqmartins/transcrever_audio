"""Diálogo simples para configurar a chave de API da Groq."""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from app.config import COLOR_INDIGO, COLOR_PANEL, GROQ_API_KEYS_URL
from app.ui.style import STYLE_SHEET
from app.ui.widgets import RoundedButton
from app.utils.settings import load_api_key, save_api_key


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(420)
        # Aplicado explicitamente (não basta herdar do pai): em alguns
        # ambientes Linux um QDialog não herda o stylesheet da janela pai e
        # aparece com o tema claro padrão do sistema.
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = QLabel(
            "A transcrição é feita pela API da Groq. Informe sua chave de API "
            f'gratuita (obtida em <a href="{GROQ_API_KEYS_URL}">{GROQ_API_KEYS_URL}</a>).'
        )
        info.setWordWrap(True)
        info.setOpenExternalLinks(True)
        layout.addWidget(info)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("gsk_...")
        saved_key = load_api_key()
        if saved_key:
            self.api_key_input.setText(saved_key)
        layout.addWidget(self.api_key_input)

        self.show_key_button = RoundedButton(
            "Mostrar", bg_color=COLOR_PANEL, hover_color="#1c2129", pressed_color=COLOR_INDIGO, radius=14
        )
        self.show_key_button.setCheckable(True)
        self.show_key_button.toggled.connect(self._toggle_visibility)

        row = QHBoxLayout()
        row.addWidget(self.show_key_button)
        row.addStretch()
        layout.addLayout(row)

        buttons_row = QHBoxLayout()
        buttons_row.addStretch()
        cancel_button = RoundedButton(
            "Cancelar", bg_color=COLOR_PANEL, hover_color="#1c2129", pressed_color=COLOR_INDIGO, radius=14
        )
        cancel_button.clicked.connect(self.reject)
        save_button = RoundedButton(
            "Salvar",
            bg_color=COLOR_INDIGO,
            hover_color="#7a7df3",
            pressed_color="#4f52c1",
            radius=14,
        )
        save_button.clicked.connect(self._on_save)
        buttons_row.addWidget(cancel_button)
        buttons_row.addWidget(save_button)
        layout.addLayout(buttons_row)

    def _toggle_visibility(self, checked: bool) -> None:
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.api_key_input.setEchoMode(mode)
        self.show_key_button.setText("Ocultar" if checked else "Mostrar")

    def _on_save(self) -> None:
        api_key = self.api_key_input.text().strip()
        if api_key:
            save_api_key(api_key)
        self.accept()

    @staticmethod
    def get_saved_api_key() -> Optional[str]:
        return load_api_key()
