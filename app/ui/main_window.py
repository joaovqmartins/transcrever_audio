"""Janela principal do Audio Transcriber: interface gráfica em PySide6."""

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config import (
    APP_NAME,
    APP_SUBTITLE,
    COLOR_ALMOND_SILK,
    COLOR_BUBBLEGUM_PINK,
    COLOR_GUNMETAL,
    COLOR_MUTED_TEAL,
    COLOR_OLD_ROSE,
    DEFAULT_MODEL_INDEX,
    LANGUAGE_OPTIONS,
    MODEL_OPTIONS,
)
from app.transcription.groq_engine import transcribe_audio
from app.ui.settings_dialog import SettingsDialog
from app.utils.audio import human_readable_size, is_supported_audio
from app.utils.settings import load_api_key


class TranscriptionWorker(QThread):
    """Executa a transcrição em uma thread separada para não travar a UI."""

    status_changed = Signal(str)
    finished_ok = Signal(str)
    failed = Signal(str)

    def __init__(self, file_path: str, api_key: str, model_id: str, language: Optional[str]):
        super().__init__()
        self.file_path = file_path
        self.api_key = api_key
        self.model_id = model_id
        self.language = language

    def run(self) -> None:
        try:
            text = transcribe_audio(
                self.file_path,
                self.api_key,
                self.model_id,
                self.language,
                on_status=self.status_changed.emit,
            )
            self.finished_ok.emit(text)
        except Exception as exc:  # captura qualquer falha da API/rede
            self.failed.emit(str(exc))


class DropArea(QFrame):
    """Área de arrastar-e-soltar; um clique também abre o seletor de arquivos."""

    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        self.setMinimumHeight(150)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(4)

        icon_label = QLabel("🎵")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 30px; border: none; background: transparent;")

        self.title_label = QLabel("Arraste seu áudio aqui")
        self.title_label.setObjectName("dropTitle")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.subtitle_label = QLabel("ou clique para selecionar (.mp3, .ogg)")
        self.subtitle_label.setObjectName("dropSubtitle")
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)

    def mousePressEvent(self, event):
        if not self.isEnabled():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar arquivo de áudio", "", "Áudio (*.mp3 *.ogg)"
        )
        if path:
            self.file_dropped.emit(path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if self.isEnabled() and event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_dragging(True)

    def dragLeaveEvent(self, event):
        self._set_dragging(False)

    def dropEvent(self, event: QDropEvent):
        self._set_dragging(False)
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path:
                self.file_dropped.emit(path)

    def _set_dragging(self, dragging: bool) -> None:
        self.setProperty("dragging", dragging)
        self.style().unpolish(self)
        self.style().polish(self)


STYLE_SHEET = f"""
QMainWindow, QWidget {{
    background-color: {COLOR_GUNMETAL};
    color: {COLOR_ALMOND_SILK};
    font-family: 'Segoe UI', sans-serif;
}}
QLabel#appTitle {{
    font-size: 21px;
    font-weight: 600;
}}
QLabel#appSubtitle {{
    font-size: 12px;
    color: {COLOR_OLD_ROSE};
}}
QFrame#dropArea {{
    border: 2px dashed {COLOR_OLD_ROSE};
    border-radius: 12px;
    background-color: rgba(213, 187, 177, 0.06);
}}
QFrame#dropArea[dragging="true"] {{
    border-color: {COLOR_MUTED_TEAL};
    background-color: rgba(156, 196, 178, 0.14);
}}
QFrame#dropArea:disabled {{
    border-color: #55595b;
}}
QLabel#dropTitle {{
    font-size: 14px;
    font-weight: 600;
    border: none;
    background: transparent;
}}
QLabel#dropSubtitle {{
    font-size: 11px;
    color: {COLOR_ALMOND_SILK};
    border: none;
    background: transparent;
}}
QLabel#fileInfo {{
    font-size: 12px;
    color: {COLOR_MUTED_TEAL};
}}
QLabel#statusLabel {{
    font-size: 12px;
}}
QLabel#sectionTitle {{
    font-size: 12px;
    font-weight: 600;
}}
QPushButton {{
    background-color: {COLOR_OLD_ROSE};
    color: {COLOR_GUNMETAL};
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}}
QPushButton:hover:!disabled {{
    background-color: {COLOR_ALMOND_SILK};
}}
QPushButton:disabled {{
    background-color: #55595b;
    color: #8a8f91;
}}
QPushButton#primaryButton {{
    background-color: {COLOR_BUBBLEGUM_PINK};
    color: white;
    font-size: 14px;
    padding: 10px 28px;
}}
QPushButton#primaryButton:hover:!disabled {{
    background-color: #ef8494;
}}
QProgressBar {{
    border: none;
    border-radius: 6px;
    background-color: #2f3234;
    text-align: center;
    color: {COLOR_ALMOND_SILK};
    min-height: 14px;
}}
QProgressBar::chunk {{
    background-color: {COLOR_MUTED_TEAL};
    border-radius: 6px;
}}
QTextEdit {{
    background-color: #2f3234;
    border: 1px solid #4a4e50;
    border-radius: 8px;
    padding: 8px;
    font-size: 13px;
}}
QComboBox {{
    background-color: #2f3234;
    border: 1px solid #4a4e50;
    border-radius: 6px;
    padding: 4px 8px;
}}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(560, 720)
        self.setStyleSheet(STYLE_SHEET)

        self.current_file: Optional[str] = None
        self.worker: Optional[TranscriptionWorker] = None
        self.transcribed_text: str = ""

        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        settings_row = QHBoxLayout()
        settings_row.addStretch()
        self.settings_button = QPushButton("⚙ Configurações")
        self.settings_button.clicked.connect(self._open_settings)
        settings_row.addWidget(self.settings_button)
        root.addLayout(settings_row)

        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setObjectName("appSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        root.addWidget(title)
        root.addWidget(subtitle)

        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self._on_file_selected)
        root.addWidget(self.drop_area)

        self.file_info_label = QLabel("Nenhum arquivo selecionado")
        self.file_info_label.setObjectName("fileInfo")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self.file_info_label)

        options_row = QHBoxLayout()
        options_row.setSpacing(16)

        model_col = QVBoxLayout()
        model_label = QLabel("Modelo")
        model_label.setObjectName("sectionTitle")
        self.model_combo = QComboBox()
        for option in MODEL_OPTIONS:
            self.model_combo.addItem(option.label)
        self.model_combo.setCurrentIndex(DEFAULT_MODEL_INDEX)
        self.model_combo.currentIndexChanged.connect(self._update_model_hint)
        model_col.addWidget(model_label)
        model_col.addWidget(self.model_combo)

        lang_col = QVBoxLayout()
        lang_label = QLabel("Idioma")
        lang_label.setObjectName("sectionTitle")
        self.language_combo = QComboBox()
        for label, _code in LANGUAGE_OPTIONS:
            self.language_combo.addItem(label)
        lang_col.addWidget(lang_label)
        lang_col.addWidget(self.language_combo)

        options_row.addLayout(model_col, stretch=1)
        options_row.addLayout(lang_col, stretch=1)
        root.addLayout(options_row)

        self.model_hint_label = QLabel("")
        self.model_hint_label.setObjectName("fileInfo")
        self.model_hint_label.setWordWrap(True)
        self.model_hint_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self.model_hint_label)
        self._update_model_hint()

        self.transcribe_button = QPushButton("Transcrever")
        self.transcribe_button.setObjectName("primaryButton")
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.clicked.connect(self._start_transcription)
        root.addWidget(self.transcribe_button, alignment=Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        root.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        root.addWidget(self.progress_bar)

        result_title = QLabel("Transcrição")
        result_title.setObjectName("sectionTitle")
        root.addWidget(result_title)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("Texto transcrito aparecerá aqui...")
        root.addWidget(self.result_text, stretch=1)

        actions_row = QHBoxLayout()
        actions_row.addStretch()
        self.copy_button = QPushButton("Copiar")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self._copy_text)
        self.save_button = QPushButton("Salvar")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._save_text)
        actions_row.addWidget(self.copy_button)
        actions_row.addWidget(self.save_button)
        root.addLayout(actions_row)

    # -- eventos de UI ----------------------------------------------------

    def _update_model_hint(self) -> None:
        option = MODEL_OPTIONS[self.model_combo.currentIndex()]
        self.model_hint_label.setText(option.description)

    def _on_file_selected(self, path: str) -> None:
        if not is_supported_audio(path):
            QMessageBox.warning(
                self,
                "Formato não suportado",
                "Por enquanto, apenas arquivos .mp3 e .ogg são suportados.",
            )
            return
        if not os.path.isfile(path):
            QMessageBox.warning(
                self, "Arquivo inválido", "Não foi possível encontrar o arquivo selecionado."
            )
            return

        self.current_file = path
        self.file_info_label.setText(f"{os.path.basename(path)} ({human_readable_size(path)})")
        self.transcribe_button.setEnabled(True)
        self.result_text.clear()
        self.transcribed_text = ""
        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.status_label.setText("")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def _set_busy(self, busy: bool) -> None:
        self.transcribe_button.setEnabled(not busy and self.current_file is not None)
        self.drop_area.setEnabled(not busy)
        self.model_combo.setEnabled(not busy)
        self.language_combo.setEnabled(not busy)
        self.settings_button.setEnabled(not busy)
        self.progress_bar.setVisible(busy)

    def _open_settings(self) -> None:
        SettingsDialog(self).exec()

    def _start_transcription(self) -> None:
        if not self.current_file:
            return

        api_key = load_api_key()
        if not api_key:
            QMessageBox.information(
                self,
                "Configure sua chave de API",
                "Você ainda não configurou uma chave de API da Groq. "
                "Clique em \"Configurações\" para informá-la.",
            )
            self._open_settings()
            return

        model_option = MODEL_OPTIONS[self.model_combo.currentIndex()]
        language_code = LANGUAGE_OPTIONS[self.language_combo.currentIndex()][1]

        self._set_busy(True)
        self.result_text.clear()
        self.transcribed_text = ""
        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # indeterminado: a API não relata progresso incremental
        self.status_label.setText("Enviando áudio...")

        self.worker = TranscriptionWorker(self.current_file, api_key, model_option.model_id, language_code)
        self.worker.status_changed.connect(self.status_label.setText)
        self.worker.finished_ok.connect(self._on_transcription_finished)
        self.worker.failed.connect(self._on_transcription_failed)
        self.worker.start()

    def _on_transcription_finished(self, text: str) -> None:
        self.transcribed_text = text
        self.result_text.setPlainText(text)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self._set_busy(False)

        has_text = bool(text.strip())
        self.copy_button.setEnabled(has_text)
        self.save_button.setEnabled(has_text)

        if has_text:
            self.status_label.setText("Concluído.")
        else:
            self.status_label.setText("Nenhuma fala identificada.")
            QMessageBox.information(
                self,
                "Nenhum texto detectado",
                "Não foi possível identificar fala no áudio enviado.",
            )

    def _on_transcription_failed(self, message: str) -> None:
        self.status_label.setText("Ocorreu um erro durante a transcrição.")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self._set_busy(False)
        QMessageBox.critical(
            self,
            "Erro na transcrição",
            f"Não foi possível transcrever o áudio:\n\n{message}",
        )

    def _copy_text(self) -> None:
        QApplication.clipboard().setText(self.transcribed_text)
        self.status_label.setText("Transcrição copiada para a área de transferência.")

    def _save_text(self) -> None:
        if not self.transcribed_text.strip():
            return

        suggested_name = "transcricao.txt"
        if self.current_file:
            base = os.path.splitext(os.path.basename(self.current_file))[0]
            suggested_name = f"{base}.txt"

        # getSaveFileName já pede confirmação nativa antes de sobrescrever um arquivo existente.
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar transcrição", suggested_name, "Arquivo de texto (*.txt)"
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(self.transcribed_text)
            self.status_label.setText(f"Transcrição salva em: {path}")
        except OSError as exc:
            QMessageBox.critical(self, "Erro ao salvar", f"Não foi possível salvar o arquivo:\n\n{exc}")
