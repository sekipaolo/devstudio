from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QPushButton, QListWidget, QCheckBox, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from .widgets import PromptInput, ConfirmButton, ResponseDisplay, StatusProgressBar, StatusLabel
from .file_tree import FileTreeView
from config.global_config import config

def setup_ui_components(main_window, layout):
    main_window.logging_checkbox = QCheckBox("Enable GUI Logging")
    main_window.logging_checkbox.setChecked(True)
    main_window.logging_checkbox.stateChanged.connect(main_window.logging_manager.toggle_logging)
    layout.addWidget(main_window.logging_checkbox)

    main_window.change_root_button = QPushButton("Change Project Root")
    main_window.change_root_button.clicked.connect(lambda: change_project_root(main_window))
    layout.addWidget(main_window.change_root_button)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    layout.addWidget(splitter)

    main_window.file_tree = FileTreeView()
    splitter.addWidget(main_window.file_tree)

    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)

    main_window.prompt_input = PromptInput()
    right_layout.addWidget(QLabel('Enter your prompt:'))
    right_layout.addWidget(main_window.prompt_input)

    button_layout = QHBoxLayout()
    main_window.confirm_button = ConfirmButton()
    main_window.confirm_button.clicked.connect(main_window.confirm_and_send)
    button_layout.addWidget(main_window.confirm_button)

    main_window.apply_changes_button = QPushButton("Apply Changes")
    main_window.apply_changes_button.clicked.connect(main_window.apply_file_changes)
    main_window.apply_changes_button.setVisible(False)
    button_layout.addWidget(main_window.apply_changes_button)

    right_layout.addLayout(button_layout)

    main_window.status_progress_bar = StatusProgressBar()
    right_layout.addWidget(main_window.status_progress_bar)

    main_window.status_label = StatusLabel()
    right_layout.addWidget(main_window.status_label)

    main_window.response_display = ResponseDisplay()
    main_window.response_display.setVisible(False)
    right_layout.addWidget(QLabel('AI Response:'))
    right_layout.addWidget(main_window.response_display)

    main_window.file_changes_list = QListWidget()
    main_window.file_changes_list.setVisible(False)
    right_layout.addWidget(QLabel('File Changes:'))
    right_layout.addWidget(main_window.file_changes_list)

    splitter.addWidget(right_panel)

def change_project_root(main_window):
    new_root = QFileDialog.getExistingDirectory(main_window, "Select Project Root Directory")
    if new_root:
        try:
            config.set("project_root", new_root)
            main_window.populate_file_tree()
            main_window.logging_manager.log('info', f"Project root changed to: {new_root}")
            QMessageBox.information(main_window, "Project Root Changed", f"Project root has been changed to:\n{new_root}")
        except Exception as e:
            main_window.logging_manager.log('error', f"Error changing project root: {str(e)}")
            QMessageBox.critical(main_window, "Error", f"Failed to change project root: {str(e)}")
