from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import re

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True",
            "try", "while", "with", "yield"
        ]
        for word in keywords:
            self.highlighting_rules.append((re.compile(f"\\b{word}\\b"), keyword_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((re.compile(r"#.*"), comment_format))

        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        self.highlighting_rules.append((re.compile(r"\bdef\s+(\w+)"), function_format))
        self.highlighting_rules.append((re.compile(r"\bclass\s+(\w+)"), function_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((re.compile(r"\b[+-]?[0-9]+[lL]?\b"), number_format))
        self.highlighting_rules.append((re.compile(r"\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b"), number_format))
        self.highlighting_rules.append((re.compile(r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b"), number_format))

        # Decorators
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#4EC9B0"))
        self.highlighting_rules.append((re.compile(r"@\w+"), decorator_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)

class FilePreviewPopup(QDialog):
    def __init__(self, file_path, content):
        super().__init__()
        self.setWindowTitle(f"File Preview: {file_path}")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel(f"File: {file_path}"))

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(content)
        layout.addWidget(self.text_edit)

        # Apply syntax highlighting for Python files
        if file_path.endswith('.py'):
            self.highlighter = PythonSyntaxHighlighter(self.text_edit.document())

        # Set a monospace font for better code readability
        font = QFont("Courier New", 10)
        self.text_edit.setFont(font)
