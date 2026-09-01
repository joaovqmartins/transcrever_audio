"""Folha de estilo (QSS) compartilhada entre a janela principal e diálogos.

Fica num módulo à parte (em vez de dentro de main_window.py) para poder ser
aplicada também no SettingsDialog: em alguns ambientes Linux, um QDialog não
herda automaticamente o stylesheet do widget pai, e acabava aparecendo com o
tema claro padrão do sistema — destoando do resto do app.
"""

from __future__ import annotations

from app.config import COLOR_INDIGO, COLOR_INK, COLOR_MIST, COLOR_PANEL, COLOR_STEEL

STYLE_SHEET = f"""
QMainWindow, QDialog {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLOR_INK}, stop:1 #10141b);
}}
QWidget#central {{
    background: transparent;
}}
QWidget {{
    color: {COLOR_MIST};
    font-family: 'Segoe UI', sans-serif;
}}
QLabel#appTitle {{
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}
QLabel#appSubtitle {{
    font-size: 12px;
    color: {COLOR_STEEL};
}}
QFrame#dropArea {{
    border: 1px dashed rgba(139, 148, 158, 0.55);
    border-radius: 20px;
    background-color: rgba(139, 148, 158, 0.05);
}}
QFrame#dropArea:hover {{
    background-color: rgba(139, 148, 158, 0.12);
}}
QFrame#dropArea[dragging="true"] {{
    border-color: {COLOR_INDIGO};
    background-color: rgba(99, 102, 241, 0.12);
}}
QFrame#dropArea[hasFile="true"] {{
    border-style: solid;
    border-color: {COLOR_INDIGO};
    background-color: rgba(99, 102, 241, 0.06);
}}
QFrame#dropArea:disabled {{
    border-color: #2a2f38;
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
    color: {COLOR_STEEL};
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
    color: {COLOR_STEEL};
}}
QPushButton {{
    background-color: {COLOR_PANEL};
    color: {COLOR_MIST};
    border: 1px solid rgba(139, 148, 158, 0.35);
    border-radius: 14px;
    padding: 8px 16px;
    font-weight: 600;
}}
QPushButton:hover:!disabled {{
    background-color: #1c2129;
    border-color: {COLOR_INDIGO};
}}
QPushButton:pressed:!disabled {{
    background-color: {COLOR_INDIGO};
    border-color: {COLOR_INDIGO};
    color: white;
}}
QPushButton:disabled {{
    background-color: #12161d;
    color: #4a4f58;
    border-color: #22262e;
}}
QPushButton#primaryButton {{
    background-color: {COLOR_INDIGO};
    color: white;
    border: none;
    font-size: 14px;
    padding: 11px 30px;
    border-radius: 24px;
}}
QPushButton#primaryButton:hover:!disabled {{
    background-color: #7a7df3;
}}
QPushButton#primaryButton:pressed:!disabled {{
    background-color: #4f52c1;
}}
QPushButton#iconButton {{
    background-color: transparent;
    border: none;
    color: {COLOR_MIST};
    border-radius: 18px;
    padding: 0px;
}}
QPushButton#iconButton:hover:!disabled {{
    background-color: rgba(230, 237, 243, 0.10);
}}
QPushButton#iconButton:pressed:!disabled {{
    background-color: rgba(230, 237, 243, 0.18);
}}
QTextEdit, QLineEdit {{
    background-color: {COLOR_INK};
    border: 1px solid rgba(139, 148, 158, 0.5);
    border-radius: 16px;
    padding: 10px 14px;
    font-size: 13px;
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {COLOR_INDIGO};
}}
QComboBox {{
    background-color: {COLOR_INK};
    border: 1px solid rgba(139, 148, 158, 0.5);
    border-radius: 14px;
    padding: 5px 10px;
}}
QComboBox:hover {{
    border-color: {COLOR_INDIGO};
}}
QComboBox::drop-down {{
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: {COLOR_PANEL};
    color: {COLOR_MIST};
    border: 1px solid rgba(139, 148, 158, 0.5);
    border-radius: 10px;
    outline: none;
    selection-background-color: {COLOR_INDIGO};
    selection-color: white;
}}
"""
