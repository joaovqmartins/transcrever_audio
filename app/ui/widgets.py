"""Widgets reutilizáveis com pequenos toques de animação para a interface."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QPushButton, QWidget


class AnimatedButton(QPushButton):
    """QPushButton com um leve efeito de "levantar" ao passar o mouse ou clicar.

    A animação só translada a posição do botão — nunca redimensiona. Um botão
    com border-radius grande no QSS (estilo "pílula") distorce visualmente se
    a altura mudar mesmo um pouco: o raio (fixo em px) passa a valer mais que
    metade da nova altura e o botão parece "virar uma bolinha". Por isso o
    tamanho fica travado (`resize` uma única vez) e só a posição anima.

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
