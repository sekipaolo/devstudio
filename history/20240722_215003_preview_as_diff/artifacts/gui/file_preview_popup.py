from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt
import re
import difflib

class DiffSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Added lines
        added_format = QTextCharFormat()
        added_format.setBackground(QColor("#144212"))
        self.highlighting_rules.append((re.compile(r"^\+.*"), added_format))

        # Removed lines
        removed_format = QTextCharFormat()
        removed_format.setBackground(QColor("#401313"))
        self.highlighting_rules.append((re.compile(r"^-.*"), removed_format))

        # Header lines
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#729FCF"))
        self.highlighting_rules.append((re.compile(r"^@@.*@@"), header_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match = pattern.search(text)
            if match:
                self.setFormat(0, len(text), format)

class FilePreviewPopup(QDialog):
    def __init__(self, file_path, old_content, new_content):
        super().__init__()
        self.setWindowTitle(f"File Diff Preview: {file_path}")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel(f"File: {file_path}"))

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # Generate and display the diff
        diff = self.generate_diff(old_content, new_content)
        self.text_edit.setPlainText(diff)

        # Apply syntax highlighting for the diff
        self.highlighter = DiffSyntaxHighlighter(self.text_edit.document())

        # Set a monospace font for better code readability
        font = QFont("Courier New", 10)
        self.text_edit.setFont(font)

    def generate_diff(self, old_content, new_content):
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        differ = difflib.Differ()
        diff = list(differ.compare(old_lines, new_lines))
        return '\n'.join(diff)
