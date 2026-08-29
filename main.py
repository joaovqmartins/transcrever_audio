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

    icon = QIcon(str(APP_ICON_PATH))
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
