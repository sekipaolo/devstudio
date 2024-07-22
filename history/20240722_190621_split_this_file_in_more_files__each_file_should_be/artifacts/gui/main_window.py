import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QPushButton, QListWidget, QCheckBox
from PyQt6.QtCore import Qt, QTimer
from .file_tree import FileTreeView
from .widgets import PromptInput, ConfirmButton, ResponseDisplay, StatusProgressBar, StatusLabel
from .ai_assistant_logic import AIAssistantLogic
from .file_changes_manager import FileChangesManager
from .logging_manager import LoggingManager
from .ui_components import setup_ui_components
from config.global_config import config

class AIAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = AIAssistantLogic()
        self.logging_manager = LoggingManager()
        self.file_changes_manager = FileChangesManager(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('AI Assistant GUI')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        setup_ui_components(self, layout)

        self.populate_file_tree()

    def populate_file_tree(self):
        self.file_tree.populate(config.get("project_root"))

    def confirm_and_send(self):
        prompt = self.prompt_input.toPlainText()
        selected_files = self.file_tree.get_selected_files()
        
        if not selected_files:
            self.logging_manager.log('error', "No files selected. Please select files before sending.")
            return

        self.status_progress_bar.setVisible(True)
        self.status_label.update_status("Sending request to AI...")
        
        QTimer.singleShot(100, lambda: self.process_ai_response(prompt, selected_files))

    def process_ai_response(self, prompt, selected_files):
        try:
            response, processor = self.logic.process_prompt(prompt, selected_files)            
            self.status_label.update_status("Processing AI response...")
            self.response_display.display_processed_response(processor.response["files"])
            self.response_display.setVisible(True)
            
            self.file_changes_manager.show_file_changes(processor)

            self.status_progress_bar.setVisible(False)
            self.status_label.update_status("AI response processed successfully!")
            
            self.apply_changes_button.setVisible(True)
            
            QTimer.singleShot(3000, lambda: self.status_label.setVisible(False))
        except Exception as e:
            self.logging_manager.log('error', f"Error processing AI response: {str(e)}")

    def apply_file_changes(self):
        self.file_changes_manager.apply_changes()
