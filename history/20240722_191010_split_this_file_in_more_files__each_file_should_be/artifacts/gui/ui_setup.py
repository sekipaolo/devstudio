from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QLabel, QCheckBox, QFileDialog, QMessageBox, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from .file_tree import FileTreeView
from .widgets import PromptInput, ConfirmButton, ResponseDisplay, StatusProgressBar, StatusLabel
from config.global_config import config

class UISetupMixin:
    def initUI(self):
        self.setWindowTitle('AI Assistant GUI')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.logging_checkbox = QCheckBox("Enable GUI Logging")
        self.logging_checkbox.setChecked(True)
        self.logging_checkbox.stateChanged.connect(self.toggle_logging)
        layout.addWidget(self.logging_checkbox)

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
        self.apply_changes_button.setVisible(False)
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

    def on_item_clicked(self, index):
        # This method is now handled in the FileTreeView class
        pass

    def apply_file_changes(self):
        try:
            self.logic.apply_file_changes()
            self.populate_file_tree()
            self.file_changes_list.clear()
            self.apply_changes_button.setVisible(False)
            QMessageBox.information(self, "Response processed", "All file changes have been saved successfully.")
            
            self.show_latest_commit()
        except Exception as e:
            self.log('error', f"Error applying file changes: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to apply file changes: {str(e)}")
