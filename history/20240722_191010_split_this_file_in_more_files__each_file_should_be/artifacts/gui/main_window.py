import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QLabel, QCheckBox, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from .file_tree import FileTreeView
from .widgets import PromptInput, ConfirmButton, ResponseDisplay, StatusProgressBar, StatusLabel, FileChangeWidget
from .file_preview_popup import FilePreviewPopup
from .ai_assistant_logic import AIAssistantLogic
from .logging_setup import setup_logging, LoggingMixin
from .file_operations import FileOperationsMixin
from .ui_setup import UISetupMixin
from config.global_config import config

class AIAssistantGUI(QMainWindow, LoggingMixin, FileOperationsMixin, UISetupMixin):
    def __init__(self):
        super().__init__()
        self.logic = AIAssistantLogic()
        self.setup_logging()
        self.initUI()

    def toggle_logging(self, state):
        self.logging_enabled = state == Qt.CheckState.Checked.value
        if self.logging_enabled:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.CRITICAL)

    def confirm_and_send(self):
        prompt = self.prompt_input.toPlainText()
        selected_files = self.get_selected_files()
        
        if not selected_files:
            self.log('error', "No files selected. Please select files before sending.")
            QMessageBox.warning(self, "No Files Selected", "Please select files before sending.")
            return

        self.status_progress_bar.setVisible(True)
        self.status_label.update_status("Sending request to AI...")
        
        QTimer.singleShot(100, lambda: self.process_ai_response(prompt, selected_files))

    def process_ai_response(self, prompt, selected_files):
        try:
            response, processor = self.logic.process_prompt(prompt, selected_files)            
            self.status_label.update_status("Processing AI response...")
            self.response_display.display_processed_response("\n".join(processor.response["text"]))
            self.response_display.setVisible(True)
            
            self.show_file_changes(processor)

            self.status_progress_bar.setVisible(False)
            self.status_label.update_status("AI response processed successfully!")
            
            self.apply_changes_button.setVisible(True)
            
            QTimer.singleShot(3000, lambda: self.status_label.setVisible(False))
        except Exception as e:
            self.log('error', f"Error processing AI response: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to process AI response: {str(e)}")
            self.status_progress_bar.setVisible(False)
            self.status_label.update_status("Error processing AI response")

    def show_file_changes(self, processor):
        self.file_changes_list.clear()
        self.logic.file_changes.clear()
        for file in processor.response["files"]:
            self.add_file_change_widget(file["path"], file["action"])
        self.file_changes_list.setVisible(True)

    def add_file_change_widget(self, file_path, change_type):
        widget = FileChangeWidget(file_path, change_type)
        widget.preview_clicked.connect(self.show_file_preview)
        
        item = QListWidgetItem(self.file_changes_list)
        item.setSizeHint(widget.sizeHint())
        
        self.file_changes_list.addItem(item)
        self.file_changes_list.setItemWidget(item, widget)
        
        self.logic.file_changes[file_path] = change_type

    def show_file_preview(self, file_path):
        change_type = self.logic.file_changes.get(file_path)

        try:
            content = self.logic.get_file_preview_content(file_path, change_type)
            popup = FilePreviewPopup(file_path, content)
            popup.exec()
        except Exception as e:
            self.log('error', f"Error showing file preview for {file_path}: {str(e)}")
            QMessageBox.warning(self, "Preview Error", f"Failed to show preview for {file_path}: {str(e)}")
