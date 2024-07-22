import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QPushButton, QListWidget, QCheckBox
from PyQt6.QtCore import Qt, QTimer
from .file_tree import FileTreeView
from .widgets import PromptInput, ConfirmButton, ResponseDisplay, StatusProgressBar, StatusLabel
from .ai_assistant_logic import AIAssistantLogic
from .file_changes_manager import FileChangesManager
from .logging_manager import LoggingManager
from .project_manager import ProjectManager

class AIAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = AIAssistantLogic()
        self.logging_manager = LoggingManager()
        self.file_changes_manager = FileChangesManager(self)
        self.project_manager = ProjectManager(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('AI Assistant GUI')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.setup_logging_checkbox(layout)
        self.setup_project_root_button(layout)
        self.setup_main_splitter(layout)

    def setup_logging_checkbox(self, layout):
        self.logging_checkbox = QCheckBox("Enable GUI Logging")
        self.logging_checkbox.setChecked(True)
        self.logging_checkbox.stateChanged.connect(self.logging_manager.toggle_logging)
        layout.addWidget(self.logging_checkbox)

    def setup_project_root_button(self, layout):
        self.change_root_button = QPushButton("Change Project Root")
        self.change_root_button.clicked.connect(self.project_manager.change_project_root)
        layout.addWidget(self.change_root_button)

    def setup_main_splitter(self, layout):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self.file_tree = FileTreeView()
        self.file_tree.clicked.connect(self.project_manager.on_item_clicked)
        self.file_tree.doubleClicked.connect(self.project_manager.on_item_double_clicked)
        splitter.addWidget(self.file_tree)

        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

    def create_right_panel(self):
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.setup_prompt_input(right_layout)
        self.setup_buttons(right_layout)
        self.setup_status_widgets(right_layout)
        self.setup_response_display(right_layout)
        self.setup_file_changes_list(right_layout)

        return right_panel

    # ... (The rest of the methods will be moved to other files)
