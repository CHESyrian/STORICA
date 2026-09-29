"""
Theme manager for STORICA application.
Handles loading and applying QSS themes.
"""

from pathlib import Path
from PyQt6.QtCore import QFile, QTextStream
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    """Central theme management for the application."""

    def __init__(self):
        """Initialize theme manager."""
        self.current_theme = "dark"
        # Get the absolute path to the themes directory
        frontend_dir = Path(__file__).parent.parent.parent
        self.themes_dir = frontend_dir / "resources" / "themes"

    def apply_theme(self, app: QApplication, theme_name: str = "dark") -> bool:
        """
        Apply the specified theme to the application.

        Args:
            app: QApplication instance
            theme_name: Name of the theme file (without .qss extension)

        Returns:
            True if theme applied successfully, False otherwise
        """
        theme_file = self.themes_dir / f"{theme_name}.qss"

        if not theme_file.exists():
            return False

        # Load the stylesheet
        style_file = QFile(str(theme_file))
        if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(style_file)
            stylesheet = stream.readAll()
            app.setStyleSheet(stylesheet)
            style_file.close()
            self.current_theme = theme_name
            return True

        return False

    def get_available_themes(self) -> list:
        """
        Get list of available theme names.

        Returns:
            List of theme names (without .qss extension)
        """
        themes = []
        if self.themes_dir.exists():
            for file in self.themes_dir.glob("*.qss"):
                themes.append(file.stem)
        return themes

    def get_current_theme(self) -> str:
        """
        Get the currently active theme name.

        Returns:
            Current theme name
        """
        return self.current_theme

    def reload_theme(self, app: QApplication) -> bool:
        """
        Reload the current theme.

        Args:
            app: QApplication instance

        Returns:
            True if theme reloaded successfully, False otherwise
        """
        return self.apply_theme(app, self.current_theme)