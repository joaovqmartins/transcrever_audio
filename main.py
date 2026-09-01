"""Ponto de entrada do Audio Transcriber."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.config import APP_ICON_PATH, APP_NAME
from app.ui.main_window import MainWindow


def _fix_windows_taskbar_icon() -> None:
    """No Windows, evita que a barra de tarefas mostre o ícone do python.exe."""
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("audiotranscriber.app")


def main() -> None:
    _fix_windows_taskbar_icon()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    # "Fusion" é o único estilo do Qt com suporte completo e consistente a
    # QSS (border-radius, cores customizadas, etc.) em qualquer plataforma —
    # os estilos nativos (Windows, GTK...) ignoram/limitam várias
    # propriedades de stylesheet, causando cantos que não arredondam
    # direito e aparência inconsistente entre Windows e Linux.
    app.setStyle("Fusion")

    icon = QIcon(str(APP_ICON_PATH))
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.resize(560, 780)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
