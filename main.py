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


def _force_dark_title_bar(window) -> None:
    """No Windows, força a barra de título nativa a ficar escura sempre.

    Por padrão essa barra segue o tema claro/escuro do Windows do usuário —
    sem isso, o app fica com uma barra de título branca "destoando" do resto
    da UI (que é sempre escura) sempre que o Windows não estiver no tema
    escuro. Usa a API do DWM (DwmSetWindowAttribute), a mesma técnica usada
    por apps como o VS Code para ter uma barra de título escura consistente.
    """
    if sys.platform != "win32":
        return

    import ctypes

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Windows 10 20H1+ e Windows 11
    DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19  # builds mais antigas do Windows 10
    hwnd = int(window.winId())
    value = ctypes.c_int(1)
    for attribute in (DWMWA_USE_IMMERSIVE_DARK_MODE, DWMWA_USE_IMMERSIVE_DARK_MODE_OLD):
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value)
        )


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
    _force_dark_title_bar(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
