from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap

from frontend.utils.constants import (
    FontSize,
    FontFamily,
    Icon,
    Color,
)
from frontend.ui.widgets import color_icon


class BrandWidget(QLabel):
    """Clickable brand header widget."""

    clicked = pyqtSignal()

    def __init__(
        self,
        logo_path: str,
        width: int = 140,
        height: int = 76, 
        parent=None,
    ):
        super().__init__(parent)

        self.setObjectName("sidebarHeader")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            self.setPixmap(
                pixmap.scaled(
                    width,
                    height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


