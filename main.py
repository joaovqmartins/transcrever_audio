"""Ponto de entrada do Audio Transcriber."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.config import APP_ICON_PATH, APP_NAME, COLOR_INK, COLOR_MIST
from app.ui.main_window import MainWindow


def _fix_windows_taskbar_icon() -> None:
    """No Windows, evita que a barra de tarefas mostre o ícone do python.exe."""
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("audiotranscriber.app")


def _hex_to_colorref(hex_color: str) -> int:
    """Converte "#rrggbb" para o formato COLORREF do Windows (0x00BBGGRR)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (b << 16) | (g << 8) | r


def _force_dark_title_bar(window) -> None:
    """No Windows, força a barra de título nativa a usar as cores do app.

    Por padrão essa barra segue o tema/cor de destaque do Windows do
    usuário — sem isso, o app fica com uma barra de título clara ou com uma
    cor de destaque aleatória (a do tema do SO) "destoando" do resto da UI.
    Usa a API do DWM (DwmSetWindowAttribute), a mesma técnica usada por apps
    como o VS Code para ter uma barra de título consistente com o tema do
    app, independente da máquina.

    DWMWA_CAPTION_COLOR/BORDER_COLOR/TEXT_COLOR só têm efeito no Windows 11
    22H2+; em versões mais antigas, o pior caso é manter só o modo escuro
    (sem as cores exatas da paleta) — degrada bem, não quebra nada.
    """
    if sys.platform != "win32":
        return

    import ctypes

    hwnd = int(window.winId())
    dwmapi = ctypes.windll.dwmapi

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Windows 10 20H1+ e Windows 11
    DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19  # builds mais antigas do Windows 10
    dark_value = ctypes.c_int(1)
    for attribute in (DWMWA_USE_IMMERSIVE_DARK_MODE, DWMWA_USE_IMMERSIVE_DARK_MODE_OLD):
        dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(dark_value), ctypes.sizeof(dark_value))

    # DWMWA_SYSTEMBACKDROP_TYPE = DWMSBT_NONE: desliga o Mica/acrílico do
    # Windows 11, que senão tinge a barra de título com o papel de parede.
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMSBT_NONE = 1
    backdrop_value = ctypes.c_int(DWMSBT_NONE)
    dwmapi.DwmSetWindowAttribute(
        hwnd, DWMWA_SYSTEMBACKDROP_TYPE, ctypes.byref(backdrop_value), ctypes.sizeof(backdrop_value)
    )

    # Desligar o Mica acima pode fazer o Windows parar de arredondar os
    # cantos externos da janela automaticamente — força de volta explicitamente.
    DWMWA_WINDOW_CORNER_PREFERENCE = 33
    DWMWCP_ROUND = 2
    corner_value = ctypes.c_int(DWMWCP_ROUND)
    dwmapi.DwmSetWindowAttribute(
        hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(corner_value), ctypes.sizeof(corner_value)
    )

    # Cores exatas da nossa paleta em vez da cor de destaque do tema do
    # Windows (que varia de máquina pra máquina). A borda usa a MESMA cor do
    # fundo (em vez do valor especial "sem borda", que nem sempre é
    # respeitado igual em todo Windows) — assim ela sempre fica "invisível",
    # mesclada com o resto da janela, independente da interpretação do SO.
    DWMWA_BORDER_COLOR = 34
    DWMWA_CAPTION_COLOR = 35
    DWMWA_TEXT_COLOR = 36

    for attribute, hex_color in (
        (DWMWA_BORDER_COLOR, COLOR_INK),
        (DWMWA_CAPTION_COLOR, COLOR_INK),
        (DWMWA_TEXT_COLOR, COLOR_MIST),
    ):
        color_value = ctypes.c_uint(_hex_to_colorref(hex_color))
        dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(color_value), ctypes.sizeof(color_value))

    # Força o Windows a recalcular/redesenhar a área não-cliente agora, em
    # vez de só na próxima vez que a janela for movida/redimensionada.
    SWP_NOMOVE, SWP_NOSIZE, SWP_NOZORDER, SWP_FRAMECHANGED = 0x0002, 0x0001, 0x0004, 0x0020
    ctypes.windll.user32.SetWindowPos(
        hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED
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
    window.show()
    _force_dark_title_bar(window)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
