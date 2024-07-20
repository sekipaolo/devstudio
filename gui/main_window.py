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
from config.global_config import config

config.set("project_root", "/home/sekipaolo/apps/agi/devstudio")

class AIAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = AIAssistantLogic()
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

        # Add button to change project root
        self.change_root_button = QPushButton("Change Project Root")
        self.change_root_button.clicked.connect(self.change_project_root)
        layout.addWidget(self.change_root_button)

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
                config.set("project_root", new_root)
                self.populate_file_tree()
                self.log('info', f"Project root changed to: {new_root}")
                QMessageBox.information(self, "Project Root Changed", f"Project root has been changed to:\n{new_root}")
            except Exception as e:
                self.log('error', f"Error changing project root: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to change project root: {str(e)}")

    def populate_file_tree(self):
        self.log('debug', "Populating file tree")
        try:
            model = self.file_tree.model()
            if model:
                model.clear()
                root = model.invisibleRootItem()
                self._populate_tree_recursive(config.get("project_root"), root)
                self.log('debug', f"File tree populated with {model.rowCount()} root items")
            else:
                raise ValueError("File tree model is not initialized")
        except Exception as e:
            self.log('error', f"Error populating file tree: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to populate file tree: {str(e)}")

    def _populate_tree_recursive(self, directory: str, parent: FileTreeItem):
        try:
            for name in sorted(os.listdir(directory)):
                if name in ['.git', '__pycache__']:
                    continue
                path = os.path.join(directory, name)
                if os.path.isdir(path):
                    folder = FileTreeItem(name, is_dir=True)
                    parent.appendRow(folder)
                    self._populate_tree_recursive(path, folder)
                else:
                    item = FileTreeItem(name)
                    parent.appendRow(item)
        except Exception as e:
            self.log('error', f"Error populating directory {directory}: {str(e)}")

    def on_item_clicked(self, index):
        # This method is now handled in the FileTreeView class
        pass

    def on_item_double_clicked(self, index):
        item = self.file_tree.model().itemFromIndex(index)
        if item.is_dir:  # It's a directory
            return
        
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, 'Rename File', 'Enter new file name:', text=old_name)
        
        if ok and new_name and new_name != old_name:
            item.setText(new_name)
            self.prompt_input.append(f"\nPlease rename the file '{old_name}' to '{new_name}'.")

    def confirm_and_send(self):
        prompt = self.prompt_input.toPlainText()
        selected_files = self.get_selected_files()
        
        if not selected_files:
            self.log('error', "No files selected. Please select files before sending.")
            QMessageBox.warning(self, "No Files Selected", "Please select files before sending.")
            return

        self.status_progress_bar.setVisible(True)
        self.status_label.update_status("Sending request to AI...")
        
        # Use QTimer to allow GUI to update before processing
        QTimer.singleShot(100, lambda: self.process_ai_response(prompt, selected_files))

    def process_ai_response(self, prompt: str, selected_files: List[Dict[str, str]]):
        try:
            response, processor = self.logic.process_prompt(prompt, selected_files)
            
            self.status_label.update_status("Processing AI response...")
            self.response_display.display_processed_response(response)
            self.response_display.setVisible(True)
            
            # Show file changes
            self.show_file_changes(processor)

            self.status_progress_bar.setVisible(False)
            self.status_label.update_status("AI response processed successfully!")
            
            # Make the Apply Changes button visible
            self.apply_changes_button.setVisible(True)
            
            # Hide status label after 3 seconds
            QTimer.singleShot(3000, lambda: self.status_label.setVisible(False))
        except Exception as e:
            self.log('error', f"Error processing AI response: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to process AI response: {str(e)}")
            self.status_progress_bar.setVisible(False)
            self.status_label.update_status("Error processing AI response")

    def get_selected_files(self) -> List[Dict[str, str]]:
        selected_files = []
        def traverse(parent: FileTreeItem):
            for row in range(parent.rowCount()):
                child = parent.child(row)
                if child.checkState() == Qt.CheckState.Checked and not child.is_dir:
                    file_path = self.get_file_path(child)
                    try:
                        with open(file_path, 'r') as file:
                            content = file.read()
                        selected_files.append({"path": file_path, "content": content})
                    except Exception as e:
                        self.log('error', f"Error reading file {file_path}: {str(e)}")
                if child.hasChildren():
                    traverse(child)
        
        root = self.file_tree.model().invisibleRootItem()
        traverse(root)
        
        return selected_files

    def get_file_path(self, item: FileTreeItem) -> str:
        path = []
        while item is not None:
            path.append(item.text())
            item = item.parent()
        return os.path.join(config.get("project_root"), *reversed(path))

    def show_file_changes(self, processor):
        self.file_changes_list.clear()
        self.logic.file_changes.clear()
        for file in processor.response["files"]:
            self.add_file_change_widget(file["path"], file["action"])
        self.file_changes_list.setVisible(True)

    def add_file_change_widget(self, file_path: str, change_type: str):
        widget = FileChangeWidget(file_path, change_type)
        widget.preview_clicked.connect(self.show_file_preview)
        
        item = QListWidgetItem(self.file_changes_list)
        item.setSizeHint(widget.sizeHint())
        
        self.file_changes_list.addItem(item)
        self.file_changes_list.setItemWidget(item, widget)
        
        self.logic.file_changes[file_path] = change_type

    def show_file_preview(self, file_path: str):
        change_type = self.logic.file_changes.get(file_path)

        try:
            content = self.logic.get_file_preview_content(file_path, change_type)
            popup = FilePreviewPopup(file_path, content)
            popup.exec()
        except Exception as e:
            self.log('error', f"Error showing file preview for {file_path}: {str(e)}")
            QMessageBox.warning(self, "Preview Error", f"Failed to show preview for {file_path}: {str(e)}")

    def apply_file_changes(self):
        try:
            self.logic.apply_file_changes()
            self.populate_file_tree()  # Refresh the file tree
            self.file_changes_list.clear()
            self.apply_changes_button.setVisible(False)  # Hide the button after changes are applied
            QMessageBox.information(self, "Response processed", "All file changes have been saved successfully.")
            
            # Show the latest git commit
            self.show_latest_commit()
        except Exception as e:
            self.log('error', f"Error applying file changes: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to apply file changes: {str(e)}")

    def get_latest_commit(self):
        try:
            result = subprocess.run(['git', 'log', '-1', '--oneline'], 
                                    cwd=config.get("project_root"),
                                    capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.log('error', f"Error getting latest git commit: {str(e)}")
            return "Unable to retrieve latest commit"

    def show_latest_commit(self):
        commit = self.get_latest_commit()
        QMessageBox.information(self, "Latest Git Commit", f"Latest commit:\n{commit}")
