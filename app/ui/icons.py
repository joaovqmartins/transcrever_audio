"""Ícones desenhados via QPainter — evita depender da fonte de emoji do sistema,
que renderiza de forma inconsistente entre plataformas e destoa do restante da UI.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QPolygonF


def _new_pixmap(size: int) -> tuple[QPixmap, QPainter]:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    return pixmap, painter


def _pen(color: str, width: float = 1.8) -> QPen:
    pen = QPen(QColor(color))
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def lock_icon(color: str, size: int = 20) -> QIcon:
    """Ícone de cadeado (botão de configurações, que só guarda a chave de API)."""
    pixmap, painter = _new_pixmap(size)
    s = size / 24

    painter.setPen(_pen(color, 1.9))
    # argola do cadeado: arco + duas pernas retas encontrando o corpo
    shackle_rect = QRectF(8 * s, 4 * s, 8 * s, 8 * s)
    painter.drawArc(shackle_rect, 0, 180 * 16)
    painter.drawLine(QPointF(8 * s, 8 * s), QPointF(8 * s, 11 * s))
    painter.drawLine(QPointF(16 * s, 8 * s), QPointF(16 * s, 11 * s))

    # corpo do cadeado
    painter.drawRoundedRect(QRectF(5 * s, 11 * s, 14 * s, 10 * s), 2.4 * s, 2.4 * s)

    # buraco da fechadura
    painter.setPen(_pen(color, 1.5))
    painter.drawEllipse(QRectF(10.8 * s, 14.3 * s, 2.4 * s, 2.4 * s))
    painter.drawLine(QPointF(12 * s, 16.3 * s), QPointF(12 * s, 18.2 * s))

    painter.end()
    return QIcon(pixmap)


def chevron_icon(color: str, pointing: str = "down", size: int = 16) -> QIcon:
    """Seta simples (▾/▴) usada no botão de expandir/recolher a transcrição."""
    pixmap, painter = _new_pixmap(size)
    painter.setPen(_pen(color, 2.2))
    s = size / 16
    if pointing == "down":
        points = [QPointF(3 * s, 5 * s), QPointF(8 * s, 11 * s), QPointF(13 * s, 5 * s)]
    else:
        points = [QPointF(3 * s, 11 * s), QPointF(8 * s, 5 * s), QPointF(13 * s, 11 * s)]
    painter.drawPolyline(QPolygonF(points))
    painter.end()
    return QIcon(pixmap)


def copy_icon(color: str, size: int = 18) -> QIcon:
    """Duas folhas sobrepostas — ícone padrão de "copiar"."""
    pixmap, painter = _new_pixmap(size)
    painter.setPen(_pen(color, 1.6))
    s = size / 18
    painter.drawRoundedRect(QRectF(6 * s, 2 * s, 10 * s, 12 * s), 2 * s, 2 * s)
    painter.drawRoundedRect(QRectF(2 * s, 5 * s, 10 * s, 12 * s), 2 * s, 2 * s)
    painter.end()
    return QIcon(pixmap)


def save_icon(color: str, size: int = 18) -> QIcon:
    """Seta para uma bandeja — ícone de "salvar/exportar"."""
    pixmap, painter = _new_pixmap(size)
    painter.setPen(_pen(color, 1.8))
    s = size / 18
    painter.drawLine(QPointF(9 * s, 2 * s), QPointF(9 * s, 11 * s))
    painter.drawPolyline(
        QPolygonF([QPointF(5 * s, 7 * s), QPointF(9 * s, 11 * s), QPointF(13 * s, 7 * s)])
    )
    painter.drawLine(QPointF(3 * s, 15 * s), QPointF(15 * s, 15 * s))
    painter.end()
    return QIcon(pixmap)


def upload_pixmap(color: str, size: int = 40) -> QPixmap:
    """Bandeja com seta para cima — ícone padrão da área de arrastar-e-soltar."""
    pixmap, painter = _new_pixmap(size)
    painter.setPen(_pen(color, 2.0))
    s = size / 24
    painter.drawLine(QPointF(12 * s, 3 * s), QPointF(12 * s, 15 * s))
    painter.drawPolyline(
        QPolygonF([QPointF(7 * s, 8 * s), QPointF(12 * s, 3 * s), QPointF(17 * s, 8 * s)])
    )
    painter.drawLine(QPointF(4 * s, 20 * s), QPointF(20 * s, 20 * s))
    painter.end()
    return pixmap
