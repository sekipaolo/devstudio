from PyQt6.QtWidgets import QTextEdit, QPushButton, QProgressBar, QLabel

class PromptInput(QTextEdit):
    pass

class ConfirmButton(QPushButton):
    def __init__(self):
        super().__init__("Send to AI")
        self.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: none;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
            QPushButton:pressed {
                background-color: #1ABC9C;
            }
        """)

class ResponseDisplay(QTextEdit):
    def display_processed_response(self, text):
        self.setPlainText(text)

class StatusProgressBar(QProgressBar):
    pass

class StatusLabel(QLabel):
    def update_status(self, text):
        self.setText(text)
