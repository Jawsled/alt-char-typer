#!/usr/bin/env python3
"""
Alt-Char Typer
A compact type-specimen keypad: every button copies a Unicode stand-in for a
character Windows refuses to allow in file or folder names.

Each specimen card shows the forbidden original struck through in red, the
stand-in glyph large, and the codepoint beneath it. The dark theme borrows
Windows' own colors: dark-mode error red for the refusal, dark-mode accent
blue for the copy action.
"""

import html
import os
import sys

from PyQt6 import QtCore, QtGui, QtWidgets

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_IMAGE = os.path.join(
    APP_DIR, "A file name cant contain any of the following characters.png"
)

# (stand-in character, the forbidden character it replaces)
STAND_INS = [
    ("꞉", ":"),
    ("／", "/"),
    ("＼", "\\"),
    ("＊", "*"),
    ("？", "?"),
    ("＜", "<"),
    ("＞", ">"),
    ("｜", "|"),
    ("“", '"'),
    ("”", '"'),
]

# Windows-dark palette: the refusal dialog's red and the system accent blue,
# in their Windows 11 dark-mode variants.
BG = "#1B1F25"
CARD = "#262B33"
CARD_HOVER = "#2B313A"
CARD_PRESS = "#21262D"
LINE = "#383E48"
LINE_HOVER = "#4A525E"
INK = "#E9ECF1"
INK_SOFT = "#A6ADB8"
MUTED = "#8A93A0"
RED = "#FF99A4"
BLUE = "#4CC2FF"
COPIED_BG = "rgba(76, 194, 255, 0.12)"
STATUS_BG = "#16191E"

MONO_STACK = "'Cascadia Mono','Consolas',monospace"

STYLESHEET = f"""
#root {{
    background: {BG};
}}
QLabel#appTitle {{
    font-size: 17px;
    font-weight: 700;
    color: {INK};
}}
QLabel#appSubtitle {{
    font-size: 12px;
    color: {INK_SOFT};
}}
QPushButton {{
    background: {CARD};
    border: 1px solid {LINE};
    border-radius: 6px;
}}
QPushButton:hover {{
    background: {CARD_HOVER};
    border-color: {LINE_HOVER};
}}
QPushButton:pressed {{
    background: {CARD_PRESS};
}}
QPushButton:focus {{
    border-color: {BLUE};
}}
QPushButton[copied="true"] {{
    background: {COPIED_BG};
    border-color: {BLUE};
}}
QLabel#bannedChar {{
    font-size: 12px;
    font-weight: 600;
}}
QLabel#glyph {{
    font-size: 44px;
    color: {INK};
}}
QLabel#code {{
    font-family: {MONO_STACK};
    font-size: 11px;
    color: {MUTED};
}}
QFrame#figure {{
    background: {CARD};
    border: 1px solid {LINE};
    border-radius: 6px;
}}
QLabel#figureImage {{
    background: transparent;
}}
QLabel#statusLabel {{
    background: {STATUS_BG};
    border-top: 1px solid {LINE};
    padding: 8px 20px;
    font-size: 12px;
    color: {INK_SOFT};
}}
"""


def codepoint(char):
    """Return the U+XXXX label for a character."""
    return f"U+{ord(char):04X}"


class SpecimenButton(QtWidgets.QPushButton):
    """A specimen card: forbidden original struck out, stand-in glyph, codepoint."""

    copied = QtCore.pyqtSignal(str, str)

    def __init__(self, stand_in, banned, parent=None):
        super().__init__(parent)
        self.stand_in = stand_in
        self.banned = banned
        self.setFixedSize(118, 116)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"Copy {stand_in} — a stand-in for '{banned}'")
        self.setAccessibleName(f"Copy {stand_in}")

        body = QtWidgets.QVBoxLayout(self)
        body.setContentsMargins(8, 10, 8, 10)
        body.setSpacing(3)

        self.banned_label = QtWidgets.QLabel(self)
        self.banned_label.setObjectName("bannedChar")
        self.banned_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.banned_label.setText(f'<font color="{RED}"><s>{html.escape(banned)}</s></font>')

        self.glyph_label = QtWidgets.QLabel(stand_in, self)
        self.glyph_label.setObjectName("glyph")

        self.code_label = QtWidgets.QLabel(codepoint(stand_in), self)
        self.code_label.setObjectName("code")

        for label in (self.banned_label, self.glyph_label, self.code_label):
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            body.addWidget(label)

        self.clicked.connect(self._on_click)

    def _on_click(self):
        """Copy the stand-in, flash the card, and announce it."""
        QtWidgets.QApplication.clipboard().setText(self.stand_in)
        self.copied.emit(self.stand_in, self.banned)
        self._set_copied(True)
        QtCore.QTimer.singleShot(700, lambda: self._set_copied(False))

    def _set_copied(self, on):
        self.setProperty("copied", on)
        style = self.style()
        style.unpolish(self)
        style.polish(self)


class AlternateCharsWindow(QtWidgets.QWidget):
    """Main window: header, specimen grid, collapsible 'why' figure, status bar."""

    def __init__(self):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("Alt-Char Typer")
        self.setStyleSheet(STYLESHEET)
        self._build()
        self.setFixedWidth(542)
        self.adjustSize()

    def _build(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 0)
        root.setSpacing(16)

        # Header
        header = QtWidgets.QVBoxLayout()
        header.setSpacing(4)
        title = QtWidgets.QLabel("Alt-Char Typer", self)
        title.setObjectName("appTitle")
        subtitle = QtWidgets.QLabel(
            "Click a character to copy it. Each one is a lookalike that "
            "Windows allows in file names.",
            self,
        )
        subtitle.setObjectName("appSubtitle")
        subtitle.setWordWrap(True)
        for label in (title, subtitle):
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            header.addWidget(label)
        root.addLayout(header)

        # Specimen grid, 4 columns
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        self.buttons = []
        for index, (stand_in, banned) in enumerate(STAND_INS):
            button = SpecimenButton(stand_in, banned, self)
            button.copied.connect(self._on_copied)
            grid.addWidget(button, index // 4, index % 4)
            self.buttons.append(button)
        root.addLayout(grid)

        # Figure: the refusal this app works around
        root.addWidget(self._build_figure(), 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

        # Status bar
        root.addStretch(1)
        self.status_label = QtWidgets.QLabel("Nothing copied yet", self)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        root.addWidget(self.status_label)

    def _build_figure(self):
        figure = QtWidgets.QFrame(self)
        figure.setObjectName("figure")
        layout = QtWidgets.QVBoxLayout(figure)
        layout.setContentsMargins(12, 12, 12, 12)

        image_label = QtWidgets.QLabel(figure)
        image_label.setObjectName("figureImage")
        image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        pixmap = QtGui.QPixmap(ERROR_IMAGE)
        if not pixmap.isNull():
            if pixmap.width() > 380 or pixmap.height() > 360:
                pixmap = pixmap.scaled(
                    380,
                    360,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation,
                )
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("Windows error dialog image not found")

        layout.addWidget(image_label)
        return figure

    def _on_copied(self, stand_in, _banned):
        self.status_label.setText(
            f'<span style="color:{BLUE};font-weight:600;">Copied</span> '
            f"{html.escape(stand_in)} "
            f'<span style="font-family:{MONO_STACK};">{codepoint(stand_in)}</span>'
        )


def main():
    """Entry point for the application."""
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Alt-Char Typer")
    app.setApplicationVersion("1.0")
    app.setFont(QtGui.QFont("Segoe UI", 9))

    # Dark palette for everything the stylesheet doesn't reach (tooltips, menus)
    palette = app.palette()
    for role, color in {
        QtGui.QPalette.ColorRole.Window: BG,
        QtGui.QPalette.ColorRole.WindowText: INK,
        QtGui.QPalette.ColorRole.Base: CARD,
        QtGui.QPalette.ColorRole.Text: INK,
        QtGui.QPalette.ColorRole.Button: CARD,
        QtGui.QPalette.ColorRole.ButtonText: INK,
        QtGui.QPalette.ColorRole.ToolTipBase: CARD,
        QtGui.QPalette.ColorRole.ToolTipText: INK,
        QtGui.QPalette.ColorRole.Highlight: BLUE,
        QtGui.QPalette.ColorRole.HighlightedText: "#10141A",
    }.items():
        palette.setColor(role, QtGui.QColor(color))
    app.setPalette(palette)

    window = AlternateCharsWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
