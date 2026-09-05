"""Widgets reutilizáveis com pequenos toques de animação para a interface."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEasingCurve, QEvent, QPoint, QPropertyAnimation, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QBitmap, QColor, QPainter, QPalette, QPen, QRegion
from PySide6.QtWidgets import QComboBox, QGraphicsDropShadowEffect, QPushButton, QWidget


def _rounded_mask(size: QSize, radius: float) -> QRegion:
    """Máscara de janela com cantos arredondados.

    Usado para o popup do QComboBox: por ser uma janela top-level própria,
    `border-radius` no QSS não recorta o fundo dela (mesma peculiaridade dos
    QPushButton — ver RoundedButton). Como não dá pra sobrescrever o
    paintEvent do popup interno do combobox, a solução é recortar a forma da
    janela de verdade com uma máscara. Máscaras de janela no Windows são
    binárias (sem anti-aliasing de verdade), então o canto fica levemente
    "serrilhado" se você olhar de perto/com zoom, mas no tamanho real da UI
    fica com aparência de canto arredondado normal.
    """
    bitmap = QBitmap(size)
    bitmap.fill(Qt.GlobalColor.color0)
    painter = QPainter(bitmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(Qt.GlobalColor.color1)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(QRectF(0, 0, size.width(), size.height()), radius, radius)
    painter.end()
    return QRegion(bitmap)


class RoundedComboBox(QComboBox):
    """QComboBox cujo menu suspenso (popup) mantém os cantos arredondados e
    um fundo escuro consistente em qualquer máquina/tema.

    O container top-level do popup (uma classe interna do Qt) não tem cor de
    fundo própria — ele só aparece com a cor certa quando o QSS/tema do
    sistema "empresta" um fundo escuro por baixo. Em outra máquina (tema
    claro do Windows, ou Linux), isso pode não acontecer, e sobra um fundo
    branco feio ao redor do conteúdo estilizado. Por isso o fundo é forçado
    aqui via `QPalette` (não depende do QSS nem do tema nativo) — e por cima
    disso, a máscara arredondada é só um acabamento visual best-effort: se o
    recorte falhar nalguma plataforma, o pior caso é um popup escuro
    quadrado, nunca um popup branco.

    O raio e a cor devem bater com `QComboBox QAbstractItemView` em
    app/ui/style.py.
    """

    POPUP_RADIUS = 10

    def __init__(self, *args, popup_bg_color: str = "#161b22", **kwargs):
        super().__init__(*args, **kwargs)
        self._popup_watched: Optional[QWidget] = None
        self._popup_bg_color = QColor(popup_bg_color)

    def showPopup(self) -> None:  # noqa: N802 (nome exigido pelo Qt)
        super().showPopup()
        popup = self.view().window()

        # O tamanho do popup pode não estar 100% definido ainda no instante em
        # que showPopup() retorna (varia entre chamada programática e clique
        # real do usuário). Aplicamos o acabamento já de cara, mas também
        # observamos eventos de Resize/Show nessa janela pra reaplicar assim
        # que o tamanho definitivo for conhecido.
        if popup is not self._popup_watched:
            popup.installEventFilter(self)
            self._popup_watched = popup

        self._style_popup(popup)

    def eventFilter(self, watched, event):  # noqa: N802 (nome exigido pelo Qt)
        if watched is self._popup_watched and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.Show,
        ):
            self._style_popup(watched)
        return super().eventFilter(watched, event)

    def _style_popup(self, popup: QWidget) -> None:
        # Fundo sólido garantido por código — a correção real do "fundo
        # branco em outra máquina", independente de QSS/tema/plataforma.
        popup.setAutoFillBackground(True)
        palette = popup.palette()
        palette.setColor(QPalette.ColorRole.Window, self._popup_bg_color)
        popup.setPalette(palette)

        if popup.size().isEmpty():
            return
        popup.setMask(_rounded_mask(popup.size(), self.POPUP_RADIUS))


class RoundedButton(QPushButton):
    """QPushButton com o fundo desenhado manualmente via QPainter.

    Nesta combinação de Qt/Windows, `border-radius` no QSS arredonda a BORDA
    de QFrame/QComboBox corretamente, mas não recorta o `background-color` de
    um QPushButton (confirmado testando cor de pixel nos cantos — o
    preenchimento continua um retângulo reto mesmo com border-radius alto).
    Para não depender dessa peculiaridade, o fundo arredondado é desenhado
    aqui à mão; o QSS cuida só da cor do texto/padding via `setStyleSheet`
    com fundo transparente.
    """

    def __init__(
        self,
        *args,
        bg_color: str,
        hover_color: Optional[str] = None,
        pressed_color: Optional[str] = None,
        disabled_color: str = "#12161d",
        text_color: str = "white",
        disabled_text_color: str = "#4a4f58",
        radius: int = 999,
        padding: str = "8px 16px",
        font_size: int = 13,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._bg = QColor(bg_color)
        self._hover = QColor(hover_color) if hover_color else self._bg.lighter(122)
        self._pressed = QColor(pressed_color) if pressed_color else self._bg.darker(125)
        self._disabled = QColor(disabled_color)
        self._radius = radius
        self._hovering = False
        self._pressing = False
        self.toggled.connect(lambda _checked: self.update())

        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; color: {text_color}; "
            f"font-weight: 600; font-size: {font_size}px; padding: {padding}; }}"
            f"QPushButton:disabled {{ color: {disabled_text_color}; }}"
        )

    def _current_color(self) -> QColor:
        if not self.isEnabled():
            return self._disabled
        if self._pressing or (self.isCheckable() and self.isChecked()):
            return self._pressed
        if self._hovering:
            return self._hover
        return self._bg

    def paintEvent(self, event) -> None:  # noqa: N802 (nome exigido pelo Qt)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        radius = min(self._radius, rect.height() / 2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._current_color())
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()
        super().paintEvent(event)

    def enterEvent(self, event):
        self._hovering = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovering = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._pressing = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressing = False
        self.update()
        super().mouseReleaseEvent(event)


class AnimatedButton(RoundedButton):
    """RoundedButton com um leve efeito de "levantar" ao passar o mouse ou clicar.

    A animação só translada a posição do botão — nunca redimensiona: mudar a
    altura mudaria o raio efetivo do fundo desenhado em `RoundedButton`,
    distorcendo o formato. Por isso o tamanho fica travado (`resize` uma
    única vez) e só a posição anima.

    O brilho (sombra) é próprio do botão e só reage ao hover/clique — nada de
    animação de pulso contínua rodando em paralelo, que só competia com o
    resto da UI (status piscando, spinner) e deixava tudo mais instável.

    Este botão deve ser inserido na UI através de `wrap_in_holder()`, que o
    coloca num contêiner sem layout próprio — assim nenhum relayout externo
    briga com a animação em andamento.
    """

    def __init__(self, *args, glow_color: str = "#000000", **kwargs):
        super().__init__(*args, **kwargs)
        self._holder_margin = 1.2
        self._base_pos = QPoint(0, 0)

        self._pos_anim = QPropertyAnimation(self, b"pos")
        self._pos_anim.setDuration(140)

        self._rest_blur = 10
        self._hover_blur = 22
        self._press_blur = 6

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 3)
        self._shadow.setBlurRadius(self._rest_blur)
        self._shadow.setColor(QColor(glow_color))
        self.setGraphicsEffect(self._shadow)

        self._shadow_anim = QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._shadow_anim.setDuration(160)

    def set_glow_color(self, color: str) -> None:
        self._shadow.setColor(QColor(color))

    def wrap_in_holder(self, margin_factor: float = 1.2) -> QWidget:
        """Envolve o botão num QWidget sem layout, com espaço extra para o "lift"."""
        self._holder_margin = margin_factor
        holder = QWidget()
        self.setParent(holder)
        self._resize_holder()
        return holder

    def setText(self, text: str) -> None:  # noqa: N802 (nome exigido pelo Qt)
        super().setText(text)
        self._resize_holder()

    def showEvent(self, event):
        super().showEvent(event)
        self._resize_holder()

    def _resize_holder(self) -> None:
        holder = self.parentWidget()
        if holder is None:
            return
        hint = self.sizeHint()
        holder.setFixedSize(
            int(hint.width() * self._holder_margin), int(hint.height() * self._holder_margin)
        )
        self.resize(hint)
        self._base_pos = QPoint(
            (holder.width() - hint.width()) // 2, (holder.height() - hint.height()) // 2
        )
        self._pos_anim.stop()
        self.move(self._base_pos)

    def _animate_to(self, dy: int, blur: int) -> None:
        easing = QEasingCurve.Type.OutBack if dy <= 0 else QEasingCurve.Type.OutCubic
        self._pos_anim.stop()
        self._pos_anim.setStartValue(self.pos())
        self._pos_anim.setEndValue(QPoint(self._base_pos.x(), self._base_pos.y() + dy))
        self._pos_anim.setEasingCurve(easing)
        self._pos_anim.start()

        self._shadow_anim.stop()
        self._shadow_anim.setStartValue(self._shadow.blurRadius())
        self._shadow_anim.setEndValue(blur)
        self._shadow_anim.start()

    def enterEvent(self, event):
        if self.isEnabled():
            self._animate_to(-3, self._hover_blur)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(0, self._rest_blur)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.isEnabled():
            self._animate_to(1, self._press_blur)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.isEnabled():
            under_mouse = self.underMouse()
            self._animate_to(-3 if under_mouse else 0, self._hover_blur if under_mouse else self._rest_blur)
        super().mouseReleaseEvent(event)


class SpinnerWidget(QWidget):
    """Indicador de carregamento circular e animado (usado enquanto transcreve)."""

    def __init__(self, color: str, size: int = 26, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._angle = 0
        self.setFixedSize(size, size)

        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._rotate)

    def start(self) -> None:
        self.show()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        self.hide()

    def _rotate(self) -> None:
        self._angle = (self._angle + 6) % 360
        self.update()

    def paintEvent(self, event):  # noqa: N802 (nome exigido pelo Qt)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(self._color)
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rect = self.rect().adjusted(2, 2, -2, -2)
        span_degrees = 100
        painter.drawArc(rect, -self._angle * 16, span_degrees * 16)
