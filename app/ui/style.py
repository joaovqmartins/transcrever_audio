"""Folha de estilo (QSS) compartilhada entre a janela principal e diálogos.

Fica num módulo à parte (em vez de dentro de main_window.py) para poder ser
aplicada também no SettingsDialog: em alguns ambientes Linux, um QDialog não
herda automaticamente o stylesheet do widget pai, e acabava aparecendo com o
tema claro padrão do sistema — destoando do resto do app.
"""

from __future__ import annotations

from app.config import COLOR_BLACK, COLOR_BROWN, COLOR_JET, COLOR_SMOKE, COLOR_TAUPE

STYLE_SHEET = f"""
QMainWindow, QDialog {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLOR_BLACK}, stop:1 #14100c);
}}
QWidget#central {{
    background: transparent;
}}
QWidget {{
    color: {COLOR_SMOKE};
    font-family: 'Segoe UI', sans-serif;
}}
QLabel#appTitle {{
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}
QLabel#appSubtitle {{
    font-size: 12px;
    color: {COLOR_TAUPE};
}}
QFrame#dropArea {{
    border: 1px dashed rgba(169, 146, 125, 0.55);
    border-radius: 14px;
    background-color: rgba(169, 146, 125, 0.05);
}}
QFrame#dropArea:hover {{
    background-color: rgba(169, 146, 125, 0.12);
}}
QFrame#dropArea[dragging="true"] {{
    border-color: {COLOR_SMOKE};
    background-color: rgba(242, 244, 243, 0.10);
}}
QFrame#dropArea[hasFile="true"] {{
    border-style: solid;
    border-color: {COLOR_SMOKE};
    background-color: rgba(242, 244, 243, 0.05);
}}
QFrame#dropArea:disabled {{
    border-color: #3a352e;
}}
QLabel#dropIcon {{
    border: none;
    background: transparent;
}}
QLabel#dropTitle {{
    font-size: 14px;
    font-weight: 600;
    border: none;
    background: transparent;
}}
QLabel#dropSubtitle {{
    font-size: 11px;
    color: {COLOR_TAUPE};
    border: none;
    background: transparent;
}}
QLabel#statusLabel {{
    font-size: 12px;
    min-height: 16px;
}}
QLabel#sectionTitle {{
    font-size: 12px;
    font-weight: 600;
    color: {COLOR_TAUPE};
}}
QPushButton {{
    background-color: {COLOR_TAUPE};
    color: {COLOR_BLACK};
    border: none;
    border-radius: 9px;
    padding: 8px 16px;
    font-weight: 600;
}}
QPushButton:hover:!disabled {{
    background-color: {COLOR_SMOKE};
}}
QPushButton:pressed:!disabled {{
    background-color: {COLOR_BROWN};
    color: {COLOR_SMOKE};
}}
QPushButton:disabled {{
    background-color: #2a2620;
    color: #6b655a;
}}
QPushButton#primaryButton {{
    background-color: {COLOR_BROWN};
    color: {COLOR_SMOKE};
    font-size: 14px;
    padding: 11px 30px;
    border-radius: 22px;
}}
QPushButton#primaryButton:hover:!disabled {{
    background-color: #968d82;
}}
QPushButton#primaryButton:pressed:!disabled {{
    background-color: #423824;
}}
QPushButton#iconButton {{
    background-color: transparent;
    border: none;
    color: {COLOR_SMOKE};
    border-radius: 18px;
    padding: 0px;
}}
QPushButton#iconButton:hover:!disabled {{
    background-color: rgba(242, 244, 243, 0.10);
}}
QPushButton#iconButton:pressed:!disabled {{
    background-color: rgba(242, 244, 243, 0.18);
}}
QTextEdit, QLineEdit {{
    background-color: {COLOR_BLACK};
    border: 1px solid {COLOR_TAUPE};
    border-radius: 10px;
    padding: 10px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border-color: {COLOR_SMOKE};
}}
QComboBox {{
    background-color: {COLOR_BLACK};
    border: 1px solid {COLOR_TAUPE};
    border-radius: 6px;
    padding: 4px 8px;
}}
QComboBox:hover {{
    border-color: {COLOR_SMOKE};
}}
QComboBox::drop-down {{
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: {COLOR_JET};
    color: {COLOR_SMOKE};
    border: 1px solid {COLOR_TAUPE};
    outline: none;
    selection-background-color: {COLOR_BROWN};
    selection-color: {COLOR_SMOKE};
}}
"""
