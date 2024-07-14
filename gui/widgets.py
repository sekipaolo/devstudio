from PyQt6.QtWidgets import QTextEdit, QPushButton, QLabel, QProgressBar, QListWidgetItem, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from ai.xml_parser import XMLParser

class PromptInput(QTextEdit):
    pass

class ConfirmButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__('Send to AI', parent)
        self.setStyleSheet("""
            background-color: #008CBA;
            color: white;
            padding: 10px;
            font-size: 16px;
        """)
        self.setMinimumHeight(50)
        self.setFont(QFont('Arial', 12))

class ResponseDisplay(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.xml_parser = XMLParser()

    def update_counts(self, input_tokens, output_tokens):
        self.setText(f"Input tokens: {input_tokens}, Output tokens: {output_tokens}")
        self.setVisible(True)

    def display_processed_response(self, response):
        processed_content = self.xml_parser.process_response(response)
        self.setText(processed_content)
        self.setVisible(True)

class StatusProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 0)  # Indeterminate progress
        self.setTextVisible(False)
        self.setVisible(False)

class StatusLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setVisible(False)

    def update_status(self, status):
        self.setText(status)
        self.setVisible(True)

class FileChangeWidget(QWidget):
    preview_clicked = pyqtSignal(str)

    def __init__(self, file_path, change_type, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.change_type = change_type

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Status icon
        self.status_icon = QLabel()
        self.set_status_icon()
        layout.addWidget(self.status_icon)

        # File path
        self.path_label = QLabel(file_path)
        layout.addWidget(self.path_label)

        # Spacer
        layout.addStretch()

        # Preview icon
        self.preview_button = QPushButton()
        self.preview_button.setIcon(QIcon("gui/icons/preview.png"))
        self.preview_button.clicked.connect(self.on_preview_clicked)
        layout.addWidget(self.preview_button)

    def set_status_icon(self):
        icon = QIcon()
        if self.change_type == "new":
            icon = QIcon("gui/icons/new.png")
        elif self.change_type == "edit":
            icon = QIcon("gui/icons/edit.png")
        elif self.change_type == "delete":
            icon = QIcon("gui/icons/delete.png")
        self.status_icon.setPixmap(icon.pixmap(24, 24))

    def on_preview_clicked(self):
        self.preview_clicked.emit(self.file_path)
