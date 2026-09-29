from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from frontend.utils.constants import Image


class StoricaWidget(QWidget):
    """Storica brand widget."""

    def __init__(
        self, 
        logo_path: str = Image.MAIN, 
        parent=None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self._pixmap = QPixmap(logo_path)
        scaled = self._pixmap.scaled(
            int(self.width()),
            int(self.height()),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setPixmap(scaled)

        layout.addStretch()
        layout.addWidget(self.logo_label)
        layout.addStretch()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_logo()

    def _update_logo(self):
        if self._pixmap.isNull():
            return

        scaled = self._pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.logo_label.setPixmap(scaled)