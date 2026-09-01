"""Janela principal do Audio Transcriber: interface gráfica em PySide6."""

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    QThread,
    QTimer,
    Signal,
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config import (
    APP_NAME,
    APP_SUBTITLE,
    AUDIO_LOADED_ICON_PATH,
    COLOR_INDIGO,
    COLOR_MIST,
    COLOR_STEEL,
    DEFAULT_MODEL_INDEX,
    LANGUAGE_OPTIONS,
    MODEL_OPTIONS,
)
from app.transcription.groq_engine import transcribe_audio
from app.ui.icons import chevron_icon, copy_icon, lock_icon, save_icon, upload_pixmap
from app.ui.settings_dialog import SettingsDialog
from app.ui.style import STYLE_SHEET
from app.ui.widgets import AnimatedButton, SpinnerWidget
from app.utils.audio import human_readable_size, is_supported_audio
from app.utils.settings import load_api_key


def _repolish(widget: QWidget) -> None:
    """Força o Qt a reaplicar o QSS depois de mudar uma dynamic property."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)


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

        self.icon_label = QLabel()
        self.icon_label.setObjectName("dropIcon")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setPixmap(upload_pixmap(COLOR_STEEL, size=44))

        self.title_label = QLabel("Arraste seu áudio aqui")
        self.title_label.setObjectName("dropTitle")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.subtitle_label = QLabel("ou clique para selecionar (.mp3, .ogg)")
        self.subtitle_label.setObjectName("dropSubtitle")
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)

        self._icon_opacity = QGraphicsOpacityEffect(self.icon_label)
        self.icon_label.setGraphicsEffect(self._icon_opacity)
        self._icon_fade_anim = QPropertyAnimation(self._icon_opacity, b"opacity", self)
        self._icon_fade_anim.setDuration(220)
        self._icon_fade_anim.setEasingCurve(QEasingCurve.OutCubic)

    def show_file(self, path: str) -> None:
        """Troca o ícone/textos para refletir o arquivo de áudio carregado."""
        pixmap = QPixmap(str(AUDIO_LOADED_ICON_PATH))
        if not pixmap.isNull():
            self.icon_label.setPixmap(
                pixmap.scaledToHeight(56, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self.icon_label.setPixmap(upload_pixmap(COLOR_STEEL, size=44))

        name = os.path.basename(path)
        elided = name if len(name) <= 42 else name[:39] + "..."
        self.title_label.setText(elided)
        self.subtitle_label.setText(f"{human_readable_size(path)} · clique para trocar")
        self.setProperty("hasFile", True)
        _repolish(self)
        self._play_icon_pop()

    def reset(self) -> None:
        self.icon_label.setPixmap(upload_pixmap(COLOR_STEEL, size=44))
        self.title_label.setText("Arraste seu áudio aqui")
        self.subtitle_label.setText("ou clique para selecionar (.mp3, .ogg)")
        self.setProperty("hasFile", False)
        _repolish(self)

    def _play_icon_pop(self) -> None:
        """Pequeno "pop" de opacidade no ícone ao trocar de arquivo."""
        self._icon_fade_anim.stop()
        self._icon_opacity.setOpacity(0.0)
        self._icon_fade_anim.setStartValue(0.0)
        self._icon_fade_anim.setEndValue(1.0)
        self._icon_fade_anim.start()

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
        _repolish(self)


_STATUS_COLORS = {
    "info": COLOR_MIST,
    "success": COLOR_STEEL,
    "error": "#f87171",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(560, 720)
        self.setStyleSheet(STYLE_SHEET)

        self.current_file: Optional[str] = None
        self.worker: Optional[TranscriptionWorker] = None
        self.transcribed_text: str = ""
        self._status_base = ""
        self._status_dot_count = 0
        self._expanded = False

        self._build_ui()

    # -- construção da interface -------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(22)

        settings_row = QHBoxLayout()
        settings_row.addStretch()
        self.settings_button = QPushButton()
        self.settings_button.setIcon(lock_icon(COLOR_MIST))
        self.settings_button.setIconSize(QSize(20, 20))
        self.settings_button.setObjectName("iconButton")
        self.settings_button.setToolTip("Configurações (chave de API)")
        self.settings_button.setFixedSize(36, 36)
        self.settings_button.setCursor(Qt.PointingHandCursor)
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

        # -- opções (modelo / idioma) --------------------------------------
        # Contêiner simples (sem fundo/borda/sombra) só para poder esconder o
        # bloco inteiro quando a transcrição é expandida.
        self.options_container = QWidget()
        options_layout = QVBoxLayout(self.options_container)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(6)

        options_row = QHBoxLayout()
        options_row.setSpacing(20)

        model_col = QVBoxLayout()
        model_col.setSpacing(6)
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
        lang_col.setSpacing(6)
        lang_label = QLabel("Idioma")
        lang_label.setObjectName("sectionTitle")
        self.language_combo = QComboBox()
        for label, _code in LANGUAGE_OPTIONS:
            self.language_combo.addItem(label)
        lang_col.addWidget(lang_label)
        lang_col.addWidget(self.language_combo)

        options_row.addLayout(model_col, stretch=1)
        options_row.addLayout(lang_col, stretch=1)
        options_layout.addLayout(options_row)
        self._update_model_hint()

        root.addWidget(self.options_container)

        # -- ação principal (transcrever / status / progresso) ------------
        self.transcribe_button = AnimatedButton("Transcrever", glow_color=COLOR_INDIGO)
        self.transcribe_button.setObjectName("primaryButton")
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.clicked.connect(self._start_transcription)

        root.addWidget(self.transcribe_button.wrap_in_holder(), alignment=Qt.AlignCenter)

        status_row = QHBoxLayout()
        status_row.setAlignment(Qt.AlignCenter)
        status_row.setSpacing(8)

        self.spinner = SpinnerWidget(COLOR_STEEL)
        self.spinner.hide()
        status_row.addWidget(self.spinner)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_opacity = QGraphicsOpacityEffect(self.status_label)
        self.status_label.setGraphicsEffect(self.status_opacity)
        self._status_fade_anim = QPropertyAnimation(self.status_opacity, b"opacity", self)
        self._status_fade_anim.setDuration(260)
        status_row.addWidget(self.status_label)

        root.addLayout(status_row)

        self._status_timer = QTimer(self)
        self._status_timer.setInterval(450)
        self._status_timer.timeout.connect(self._tick_status_dots)

        self._reveal_timer = QTimer(self)
        self._reveal_timer.setInterval(12)
        self._reveal_timer.timeout.connect(self._reveal_tick)
        self._reveal_full_text = ""
        self._reveal_pos = 0
        self._reveal_chunk = 1

        # -- resultado -------------------------------------------------
        result_title_row = QHBoxLayout()
        result_title = QLabel("Transcrição")
        result_title.setObjectName("sectionTitle")
        result_title_row.addWidget(result_title)
        result_title_row.addStretch()

        self.expand_button = QPushButton()
        self.expand_button.setIcon(chevron_icon(COLOR_MIST, "down"))
        self.expand_button.setIconSize(QSize(16, 16))
        self.expand_button.setObjectName("iconButton")
        self.expand_button.setToolTip("Expandir a área de transcrição")
        self.expand_button.setFixedSize(28, 28)
        self.expand_button.setCursor(Qt.PointingHandCursor)
        self.expand_button.clicked.connect(self._toggle_expand)
        result_title_row.addWidget(self.expand_button)

        root.addLayout(result_title_row)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("Texto transcrito aparecerá aqui...")
        root.addWidget(self.result_text, stretch=1)

        actions_row = QHBoxLayout()
        actions_row.addStretch()
        self.copy_button = QPushButton(" Copiar")
        self.copy_button.setIcon(copy_icon(COLOR_MIST))
        self.copy_button.setIconSize(QSize(15, 15))
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self._copy_text)
        self.save_button = QPushButton(" Salvar")
        self.save_button.setIcon(save_icon(COLOR_MIST))
        self.save_button.setIconSize(QSize(15, 15))
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._save_text)
        actions_row.addWidget(self.copy_button)
        actions_row.addWidget(self.save_button)
        root.addLayout(actions_row)

    # -- animações ----------------------------------------------------------

    def _reveal_text(self, text: str) -> None:
        """Revela o texto transcrito aos poucos, como se estivesse sendo digitado."""
        self._reveal_timer.stop()
        self.result_text.clear()

        self._reveal_full_text = text
        self._reveal_pos = 0
        if not text:
            return

        steps = 50
        self._reveal_chunk = max(1, len(text) // steps)
        self._reveal_timer.start()

    def _reveal_tick(self) -> None:
        self._reveal_pos = min(len(self._reveal_full_text), self._reveal_pos + self._reveal_chunk)
        self.result_text.setPlainText(self._reveal_full_text[: self._reveal_pos])
        cursor = self.result_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.result_text.setTextCursor(cursor)

        if self._reveal_pos >= len(self._reveal_full_text):
            self._reveal_timer.stop()

    # -- status ---------------------------------------------------------

    def _set_status(self, text: str, kind: str = "info") -> None:
        self._status_base = text
        self._status_dot_count = 0
        color = _STATUS_COLORS.get(kind, COLOR_MIST)
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_label.setText(text)

        self._status_fade_anim.stop()
        self.status_opacity.setOpacity(0.0)
        self._status_fade_anim.setStartValue(0.0)
        self._status_fade_anim.setEndValue(1.0)
        self._status_fade_anim.start()

    def _clear_status(self) -> None:
        self._status_timer.stop()
        self._status_base = ""
        self._status_dot_count = 0
        self.status_opacity.setOpacity(1.0)
        self.status_label.setStyleSheet(f"color: {COLOR_MIST};")
        self.status_label.setText("")

    def _tick_status_dots(self) -> None:
        self._status_dot_count = (self._status_dot_count + 1) % 4
        self.status_label.setText(self._status_base + "." * self._status_dot_count)

    # -- eventos de UI ----------------------------------------------------

    def _update_model_hint(self) -> None:
        option = MODEL_OPTIONS[self.model_combo.currentIndex()]
        self.model_combo.setToolTip(option.description)

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
        self.drop_area.show_file(path)

        self.transcribe_button.setEnabled(True)
        self._reveal_timer.stop()
        self.result_text.clear()
        self.transcribed_text = ""
        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self._clear_status()

    def _set_busy(self, busy: bool) -> None:
        self.transcribe_button.setEnabled(not busy and self.current_file is not None)
        self.transcribe_button.setText("Transcrevendo..." if busy else "Transcrever")
        self.drop_area.setEnabled(not busy)
        self.model_combo.setEnabled(not busy)
        self.language_combo.setEnabled(not busy)
        self.settings_button.setEnabled(not busy)

        if busy:
            self.spinner.start()
            self._status_timer.start()
        else:
            self.spinner.stop()
            self._status_timer.stop()

    def _open_settings(self) -> None:
        SettingsDialog(self).exec()

    def _toggle_expand(self) -> None:
        """Esconde a área de arrastar/opções para dar mais espaço à transcrição."""
        self._expanded = not self._expanded

        self.drop_area.setVisible(not self._expanded)
        self.options_container.setVisible(not self._expanded)

        if self._expanded:
            self.expand_button.setIcon(chevron_icon(COLOR_MIST, "up"))
            self.expand_button.setToolTip("Recolher a área de transcrição")
        else:
            self.expand_button.setIcon(chevron_icon(COLOR_MIST, "down"))
            self.expand_button.setToolTip("Expandir a área de transcrição")

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
        self._reveal_timer.stop()
        self.result_text.clear()
        self.transcribed_text = ""
        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self._set_status("Enviando áudio", "info")

        self.worker = TranscriptionWorker(self.current_file, api_key, model_option.model_id, language_code)
        self.worker.status_changed.connect(lambda text: self._set_status(text, "info"))
        self.worker.finished_ok.connect(self._on_transcription_finished)
        self.worker.failed.connect(self._on_transcription_failed)
        self.worker.start()

    def _on_transcription_finished(self, text: str) -> None:
        self.transcribed_text = text
        self._reveal_text(text)
        self._set_busy(False)

        has_text = bool(text.strip())
        self.copy_button.setEnabled(has_text)
        self.save_button.setEnabled(has_text)

        if has_text:
            self._set_status("Concluído.", "success")
        else:
            self._set_status("Nenhuma fala identificada.", "info")
            QMessageBox.information(
                self,
                "Nenhum texto detectado",
                "Não foi possível identificar fala no áudio enviado.",
            )

    def _on_transcription_failed(self, message: str) -> None:
        self._set_status("Ocorreu um erro durante a transcrição.", "error")
        self._set_busy(False)
        QMessageBox.critical(
            self,
            "Erro na transcrição",
            f"Não foi possível transcrever o áudio:\n\n{message}",
        )

    def _copy_text(self) -> None:
        QApplication.clipboard().setText(self.transcribed_text)
        self._set_status("Transcrição copiada para a área de transferência.", "success")

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
            self._set_status(f"Transcrição salva em: {path}", "success")
        except OSError as exc:
            QMessageBox.critical(self, "Erro ao salvar", f"Não foi possível salvar o arquivo:\n\n{exc}")
