from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor


def color_icon(path, color):
    pixmap = QPixmap(path)

    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()

    return QIcon(pixmap)