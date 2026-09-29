"""
Sidebar navigation component for STORICA using QListWidget.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap

from frontend.utils.signals import signals
from frontend.utils.config import APP_NAME
from frontend.utils.constants import (
    FontSize,
    FontFamily,
    Icon,
    Color,
    Image,
)
from frontend.ui.widgets import color_icon, BrandWidget


class Sidebar(QWidget):
    """Sidebar navigation with icons and user info footer."""

    nav_clicked = pyqtSignal(str)
    about_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.menu_items: dict[str, QListWidgetItem] = {}

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the sidebar UI."""
        self.setObjectName("sidebar")
        self.setFixedWidth(200)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._setup_header(layout)
        self._setup_nav_list(layout)
        self._setup_footer(layout)

    def _setup_header(self, layout: QVBoxLayout):
        """Setup brand header."""
        width  = int(self.width())
        height = int(width / 3)
        self.brand_widget = BrandWidget(
            logo_path=Image.BRAND,
            width=width,
            height=height
        )

        layout.addWidget(self.brand_widget)

    def _setup_nav_list(self, layout: QVBoxLayout):
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        self.nav_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.nav_list.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
        self.nav_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.nav_list.setSpacing(4)

        menu_items = [
            ("inventory", Icon.BOXES, "Inventory"),
            ("purchases", Icon.BANKNOTE_ARROW_DOWN, "Purchases"),
            ("sales", Icon.SHOPPING_CART, "Sales"),
            ("users", Icon.USERS, "Users"),
            ("panel", Icon.PANEL, "Panel"),
        ]

        for item_id, icon_path, text in menu_items:
            self._add_menu_item(
                item_id,
                icon_path,
                Color.ACCENT2,
                text,
            )

        layout.addWidget(self.nav_list, stretch=1)

    def _setup_footer(self, layout: QVBoxLayout):
        footer = QWidget()
        footer.setObjectName("sidebarFooter")

        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(12, 10, 12, 15)
        footer_layout.setSpacing(10)

        self.user_container = QWidget()
        self.user_container.setObjectName("userContainer")

        user_layout = QVBoxLayout(self.user_container)
        user_layout.setContentsMargins(12, 12, 12, 12)
        user_layout.setSpacing(5)

        # UserName -------------------------------------
        self.user_name_label = QLabel("User")
        self.user_name_label.setObjectName("userName")
        self.user_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_font = QFont(FontFamily.SEGOE)
        name_font.setPointSize(FontSize.FONT_SIZE_12)
        name_font.setWeight(QFont.Weight.Medium)

        self.user_name_label.setFont(name_font)

        # UserRole -------------------------------------
        self.user_role_label = QLabel()
        self.user_role_label.setObjectName("userRole")
        self.user_role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_role_label.setVisible(False)

        role_font = QFont(FontFamily.SEGOE)
        role_font.setPointSize(FontSize.FONT_SIZE_10)

        self.user_role_label.setFont(role_font)

        # About Button -------------------------------------
        self.about_btn = QPushButton(f"About {APP_NAME}")
        self.about_btn.setObjectName("aboutButton")
        self.about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        about_font = QFont(FontFamily.SEGOE)
        about_font.setPointSize(FontSize.FONT_SIZE_10)
        about_font.setWeight(QFont.Weight.Medium)
        self.about_btn.setFont(about_font)

        # Logout Button -------------------------------------
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setObjectName("logoutButton")
        self.logout_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        if hasattr(Icon, "LOG_OUT"):
            self.logout_btn.setIcon(
                color_icon(
                    Icon.LOG_OUT,
                    Color.COLOR_RE04,
                )
            )
            self.logout_btn.setIconSize(QSize(26, 26))

        logout_font = QFont(FontFamily.SEGOE)
        logout_font.setPointSize(FontSize.FONT_SIZE_12)
        logout_font.setWeight(QFont.Weight.Medium)

        self.logout_btn.setFont(logout_font)

        #Layouts
        user_layout.addWidget(self.user_name_label)
        user_layout.addWidget(self.user_role_label)

        footer_layout.addWidget(self.user_container)
        footer_layout.addWidget(self.about_btn)
        footer_layout.addWidget(self.logout_btn)

        layout.addWidget(footer)

    def _add_menu_item(
        self,
        item_id: str,
        icon_path: str,
        icon_color: str,
        text: str,
    ):
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, item_id)

        if icon_path:
            icon = color_icon(icon_path, icon_color)
            if not icon.isNull():
                item.setIcon(icon)

        font = QFont(FontFamily.SEGOE)
        font.setPointSize(FontSize.FONT_SIZE_10)
        font.setWeight(QFont.Weight.Medium)

        item.setFont(font)
        item.setSizeHint(QSize(0, 42))

        self.nav_list.addItem(item)
        self.menu_items[item_id] = item

    def connect_signals(self):
        self.nav_list.itemClicked.connect(
            self._on_item_clicked
        )

        self.about_btn.clicked.connect(self.about_clicked.emit)
        self.logout_btn.clicked.connect(
            lambda: self.nav_clicked.emit("logout")
        )

        self.brand_widget.clicked.connect(
            signals.brand_clicked
        )

    def _on_item_clicked(self, item: QListWidgetItem):
        item_id = item.data(Qt.ItemDataRole.UserRole)

        if item_id:
            self.set_active_item(item_id)
            self.nav_clicked.emit(item_id)

    def set_active_item(self, item_id: str):
        """Set the active/selected item in the nav list."""
        if item_id in self.menu_items:
            self.nav_list.setCurrentItem(
                self.menu_items[item_id]
            )

    def set_user_info(
        self,
        username: str,
        role: str = "",
    ):
        """Update user display name, role, and initials."""

        self.user_name_label.setText(username)

        if role:
            self.user_role_label.setText(role.capitalize())
            self.user_role_label.setVisible(True)
            
        else:
            self.user_role_label.setVisible(False)