import os
import logging
import subprocess
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
         QSplitter, QInputDialog, QLabel, QTextEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QCheckBox, QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from .file_tree import FileTreeView, FileTreeItem
from .widgets import (PromptInput, ConfirmButton, ResponseDisplay, StatusProgressBar, StatusLabel, FileChangeWidget)
from .file_preview_popup import FilePreviewPopup
from .ai_assistant_logic import AIAssistantLogic

class AIAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = AIAssistantLogic("/home/sekipaolo/apps/agi/devstudio")
        self.setup_logging()
        self.initUI()

    def setup_logging(self):
        self.logger = logging.getLogger('GUI')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logging_enabled = True

    def toggle_logging(self, state):
        self.logging_enabled = state == Qt.CheckState.Checked.value
        if self.logging_enabled:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.CRITICAL)

    def log(self, level, message):
        if self.logging_enabled:
            if level == 'debug':
                self.logger.debug(message)
            elif level == 'info':
                self.logger.info(message)
            elif level == 'warning':
                self.logger.warning(message)
            elif level == 'error':
                self.logger.error(message)
            elif level == 'critical':
                self.logger.critical(message)

    def initUI(self):
        self.setWindowTitle('AI Assistant GUI')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Add logging toggle checkbox
        self.logging_checkbox = QCheckBox("Enable GUI Logging")
        self.logging_checkbox.setChecked(True)
        self.logging_checkbox.stateChanged.connect(self.toggle_logging)
        layout.addWidget(self.logging_checkbox)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()

        # Add button to change project root
        self.change_root_button = QPushButton("Change Project Root")
        self.change_root_button.clicked.connect(self.change_project_root)
        button_layout.addWidget(self.change_root_button)

        # Add button for git rollback
        self.rollback_button = QPushButton("Rollback Latest Commit")
        self.rollback_button.clicked.connect(self.rollback_latest_commit)
        button_layout.addWidget(self.rollback_button)

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self.file_tree = FileTreeView()
        self.file_tree.clicked.connect(self.on_item_clicked)
        self.file_tree.doubleClicked.connect(self.on_item_double_clicked)
        splitter.addWidget(self.file_tree)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.prompt_input = PromptInput()
        right_layout.addWidget(QLabel('Enter your prompt:'))
        right_layout.addWidget(self.prompt_input)

        button_layout = QHBoxLayout()
        self.confirm_button = ConfirmButton()
        self.confirm_button.clicked.connect(self.confirm_and_send)
        self.confirm_button.setStyleSheet("""
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
        button_layout.addWidget(self.confirm_button)

        self.apply_changes_button = QPushButton("Apply Changes")
        self.apply_changes_button.clicked.connect(self.apply_file_changes)
        self.apply_changes_button.setStyleSheet("""
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
        self.apply_changes_button.setVisible(False)  # Initially hide the button
        button_layout.addWidget(self.apply_changes_button)

        right_layout.addLayout(button_layout)

        self.status_progress_bar = StatusProgressBar()
        right_layout.addWidget(self.status_progress_bar)

        self.status_label = StatusLabel()
        right_layout.addWidget(self.status_label)

        self.response_display = ResponseDisplay()
        self.response_display.setVisible(False)
        right_layout.addWidget(QLabel('AI Response:'))
        right_layout.addWidget(self.response_display)

        self.file_changes_list = QListWidget()
        self.file_changes_list.setVisible(False)
        right_layout.addWidget(QLabel('File Changes:'))
        right_layout.addWidget(self.file_changes_list)

        splitter.addWidget(right_panel)

        self.populate_file_tree()

    def change_project_root(self):
        new_root = QFileDialog.getExistingDirectory(self, "Select Project Root Directory")
        if new_root:
            try:
                self.logic.change_project_folder(new_root)
                self.populate_file_tree()
                self.log('info', f"Project root changed to: {new_root}")
                QMessageBox.information(self, "Project Root Changed", f"Project root has been changed to:\n{new_root}")
            except Exception as e:
                self.log('error', f"Error changing project root: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to change project root: {str(e)}")

    def rollback_latest_commit(self):
        try:
            result = subprocess.run(['git', 'reset', '--hard', 'HEAD~1'], 
                                    cwd=self.logic.project_folder,
                                    capture_output=True, text=True, check=True)
            self.log('info', f"Git rollback successful: {result.stdout}")
            QMessageBox.information(self, "Rollback Successful", "The latest commit has been rolled back successfully.")
            self.populate_file_tree()  # Refresh the file tree after rollback
        except subprocess.CalledProcessError as e:
            self.log('error', f"Error rolling back git commit: {e.stderr}")
            QMessageBox.critical(self, "Rollback Error", f"Failed to rollback the latest commit:\n{e.stderr}")

    # ... (rest of the class implementation remains unchanged)
