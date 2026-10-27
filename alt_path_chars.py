#!/usr/bin/env python3
"""
Alternative Characters for Directory Paths GUI App
Calculator-style button interface - each character is a button that copies to clipboard.
PNG image embedded at the bottom.
"""

import sys
import os
from PyQt6 import QtWidgets, QtCore, QtGui


# Characters for the buttons: ꞉ ／ ＼ ＊ ？ ＜ ＞ ｜
ALTERNATE_CHARS = {
    '꞉': 'U+A789 LATIN LETTER WITH STROKE',
    '／': 'U+FF0F FULL SOLIDUS',
    '＼': 'U+FF3C FULL REVERSE SOLIDUS',
    '＊': 'U+FF0A FULL ASTERISK',
    '？': 'U+FF1F FULL QUESTION MARK',
    '＜': 'U+FF1C FULL LESS-THAN SIGN',
    '＞': 'U+FF1E FULL GREATER-THAN SIGN',
    '｜': 'U+FF5C FULL VERTICAL LINE',
}

# Problematic characters for Windows filenames
PROBLEM_CHARS = set('<>:"|?*')


class CharButton(QtWidgets.QPushButton):
    """A button that displays a character and copies it to clipboard when clicked."""

    def __init__(self, char, description, parent=None):
        super().__init__(parent)
        self.char = char
        self.description = description
        self.setText(char)
        self.setFixedSize(80, 60)
        font = self.font()
        font.setPointSize(24)
        self.setFont(font)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                font-weight: bold;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #353535;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #202020;
                border-color: #444444;
            }
        """
        )
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        """Copy the character to clipboard and show feedback."""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.char)

        # Show temporary feedback
        original_text = self.text()
        self.setText("✓")
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                font-weight: bold;
                color: white;
            }
        """
        )

        # Reset after 1 second
        QtCore.QTimer.singleShot(1000, self._reset_button)

        # Update status bar / result label in main window
        self.parent().status_label.setText(
            f"Copied: '{self.char}' (U+{ord(self.char):04X})"
        )

    def _reset_button(self):
        """Reset the button appearance."""
        self.setText(self.char)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                font-weight: bold;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #353535;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #202020;
                border-color: #444444;
            }
        """
        )


class AlternateCharsWindow(QtWidgets.QWidget):
    """Main window for the alternate characters app."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alternative Characters for Directory Paths")
        self.resize(500, 600)
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        main_layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Alternative Characters for Directory Paths")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 8px; color: #ffffff;")
        main_layout.addWidget(title)

        # Instructions
        instructions = QtWidgets.QLabel(
            "Click any character button to copy it to the clipboard."
        )
        instructions.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("margin: 0 16px; color: #bbbbbb;")
        main_layout.addWidget(instructions)

        # Buttons grid - calculator style
        grid_layout = QtWidgets.QGridLayout()

        # Define button layout (rows x cols)
        # 8 buttons in a 4-column x 2-row keypad layout
        char_items = list(ALTERNATE_CHARS.items())
        columns = 4

        for index, (char, description) in enumerate(char_items):
            row = index // columns
            col = index % columns
            btn = CharButton(char, description, self)
            grid_layout.addWidget(btn, row, col)

        main_layout.addLayout(grid_layout)

        # Status label at bottom before image
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "padding: 8px; background-color: #2b2b2b; color: #ffffff; border-top: 1px solid #555555;"
        )
        main_layout.addWidget(self.status_label)

        # Embed PNG image at the bottom
        self._embed_png(main_layout)

    def _embed_png(self, parent_layout):
        """Embed the PNG image at the bottom of the UI."""
        png_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "A file name cant contain any of the following characters.png",
        )

        if os.path.exists(png_path):
            # Load and display the PNG
            pixmap = QtGui.QPixmap(png_path)
            if not pixmap.isNull():
                # Scale pixmap to reasonable size while maintaining aspect ratio
                scaled = pixmap.scaled(
                    400, 150,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation,
                )

                image_widget = QtWidgets.QLabel()
                image_widget.setPixmap(scaled)
                image_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                image_widget.setStyleSheet(
                    "border: 1px solid #555555; margin: 4px; background-color: #1e1e1e;"
                )

                parent_layout.addWidget(image_widget, 0, QtCore.Qt.AlignmentFlag.AlignBottom)
            else:
                self._show_missing_image_placeholder(parent_layout)
        else:
            self._show_missing_image_placeholder(parent_layout)

    def _show_missing_image_placeholder(self, parent_layout):
        """Show a placeholder when PNG is not found."""
        placeholder = QtWidgets.QLabel(
            "📸 Image: 'A file name cant contain any of the following characters.png'\n"
            "(not found - showing placeholder)"
        )
        placeholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(
            "padding: 20px; background-color: #2b2b2b; border: 2px dashed #888; color: #cccccc;"
        )
        parent_layout.addWidget(placeholder)


def main():
    """Entry point for the application."""
    app = QtWidgets.QApplication(sys.argv)

    # Set a dark palette so the window background is not white
    palette = app.palette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#1e1e1e"))
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("#ffffff"))
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor("#2b2b2b"))
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("#ffffff"))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#2b2b2b"))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor("#ffffff"))
    app.setPalette(palette)

    # Set application properties
    app.setApplicationName("Alt-PathChars")
    app.setApplicationVersion("1.0")

    window = AlternateCharsWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()