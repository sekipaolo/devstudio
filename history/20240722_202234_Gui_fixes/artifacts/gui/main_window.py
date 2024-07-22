import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QPushButton, QListWidget, QCheckBox, QLineEdit, QMessageBox, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from .file_tree import FileTreeView
from .widgets import PromptInput, ConfirmButton, ResponseDisplay, StatusProgressBar, StatusLabel
from .file_changes import FileChangesList
from .ai_assistant_logic import AIAssistantLogic
from .logging_setup import setup_logging, LoggingToggle
from .project_root import ProjectRootManager
from config.global_config import config
from .file_preview_popup import FilePreviewPopup
import subprocess

class AIAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        config.set("project_root", "/home/sekipaolo/apps/agi/devstudio")
        self.logic = AIAssistantLogic()
        self.logger = setup_logging()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('AI Assistant GUI')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.logging_toggle = LoggingToggle(self.logger)
        layout.addWidget(self.logging_toggle)

        self.project_root_manager = ProjectRootManager(self)
        layout.addWidget(self.project_root_manager.change_root_button)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self.file_tree = FileTreeView()
        splitter.addWidget(self.file_tree)

        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        self.populate_file_tree()

    def create_right_panel(self):
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        change_name_layout = QHBoxLayout()
        change_name_layout.addWidget(QLabel('Change name:'))
        self.change_name_input = QLineEdit()
        change_name_layout.addWidget(self.change_name_input)
        right_layout.addLayout(change_name_layout)

        right_layout.addWidget(QLabel('Enter your prompt:'))
        self.prompt_input = PromptInput()
        self.prompt_input.setMaximumHeight(100)  # Make the prompt input smaller
        right_layout.addWidget(self.prompt_input)

        button_layout = QHBoxLayout()
        self.confirm_button = ConfirmButton()
        self.confirm_button.clicked.connect(self.confirm_and_send)
        button_layout.addWidget(self.confirm_button)

        self.apply_changes_button = QPushButton("Apply Changes")
        self.apply_changes_button.clicked.connect(self.apply_file_changes)
        self.apply_changes_button.setVisible(False)
        button_layout.addWidget(self.apply_changes_button)

        self.rollback_button = QPushButton("Rollback to Last Commit")
        self.rollback_button.clicked.connect(self.rollback_to_last_commit)
        self.rollback_button.setVisible(False)
        button_layout.addWidget(self.rollback_button)

        right_layout.addLayout(button_layout)

        self.status_progress_bar = StatusProgressBar()
        right_layout.addWidget(self.status_progress_bar)

        self.status_label = StatusLabel()
        right_layout.addWidget(self.status_label)

        self.response_display = ResponseDisplay()
        self.response_display.setVisible(False)
        right_layout.addWidget(QLabel('AI Response:'))
        right_layout.addWidget(self.response_display)

        self.file_changes_list = FileChangesList(self)
        right_layout.addWidget(QLabel('File Changes:'))
        right_layout.addWidget(self.file_changes_list)

        # Create an overlay for the status message
        self.status_overlay = QFrame(self.prompt_input)
        self.status_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")
        self.status_overlay.setVisible(False)
        overlay_layout = QVBoxLayout(self.status_overlay)
        self.overlay_label = QLabel("Sending request to AI...")
        self.overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        overlay_layout.addWidget(self.overlay_label)

        return right_panel

    def populate_file_tree(self):
        self.logger.debug("Populating file tree")
        self.file_tree.populate(config.get("project_root"))

    def confirm_and_send(self):
        prompt = self.prompt_input.toPlainText()
        selected_files = self.file_tree.get_selected_files()
        
        if not selected_files:
            self.logger.error("No files selected. Please select files before sending.")
            return

        change_name = self.change_name_input.text()
        config.set("change_name", change_name.replace(" ", "_" ))
        self.change_name_input.clear()

        self.status_progress_bar.setVisible(True)
        self.status_overlay.setVisible(True)
        self.confirm_button.setEnabled(False)
        
        QTimer.singleShot(100, lambda: self.process_ai_response(prompt, selected_files))

    def process_ai_response(self, prompt, selected_files):
        try:
            response, processor = self.logic.process_prompt(prompt, selected_files)            
            self.overlay_label.setText("Processing AI response...")
            self.response_display.display_processed_response("\n".join(processor.response["text"]))
            self.response_display.setVisible(True)
            
            self.file_changes_list.show_file_changes(processor)

            self.status_progress_bar.setVisible(False)
            self.status_overlay.setVisible(False)
            self.confirm_button.setEnabled(True)
            self.status_label.update_status("AI response processed successfully!")
            
            self.apply_changes_button.setVisible(True)
            
            QTimer.singleShot(3000, lambda: self.status_label.setVisible(False))
        except Exception as e:
            self.logger.error(f"Error processing AI response: {str(e)}")
            self.status_progress_bar.setVisible(False)
            self.status_overlay.setVisible(False)
            self.confirm_button.setEnabled(True)
            self.status_label.update_status("Error processing AI response")

    def apply_file_changes(self):
        try:
            self.logic.apply_file_changes()
            self.populate_file_tree()
            self.file_changes_list.clear()
            self.apply_changes_button.setVisible(False)
            self.rollback_button.setVisible(True)
            self.project_root_manager.show_latest_commit()
        except Exception as e:
            self.logger.error(f"Error applying file changes: {str(e)}")

    def show_file_preview(self, file_path, content):
        preview = FilePreviewPopup(file_path, content)
        preview.exec()

    def rollback_to_last_commit(self):
        try:
            # Check for uncommitted changes
            result = subprocess.run(["git", "status", "--porcelain"], cwd=config.get("project_root"), capture_output=True, text=True)
            if result.stdout.strip():
                # There are uncommitted changes
                reply = QMessageBox.question(self, 'Uncommitted Changes',
                                             "There are uncommitted changes. Do you want to discard them and hard reset?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    # Perform hard reset
                    subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=config.get("project_root"), check=True)
                    subprocess.run(["git", "clean", "-fd"], cwd=config.get("project_root"), check=True)
                else:
                    return  # User chose not to reset

            # Rollback to the last commit
            subprocess.run(["git", "reset", "--hard", "HEAD~1"], cwd=config.get("project_root"), check=True)
            
            self.populate_file_tree()
            self.rollback_button.setVisible(False)
            self.status_label.update_status("Successfully rolled back to the last commit")
            QTimer.singleShot(3000, lambda: self.status_label.setVisible(False))
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error rolling back to last commit: {str(e)}")
            self.status_label.update_status("Error rolling back to last commit")
        except Exception as e:
            self.logger.error(f"Unexpected error during rollback: {str(e)}")
            self.status_label.update_status("Unexpected error during rollback")
