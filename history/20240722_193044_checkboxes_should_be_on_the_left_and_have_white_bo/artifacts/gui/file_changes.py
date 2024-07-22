from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QWidget, QLabel, QCheckBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPalette, QColor

class FileChangeWidget(QWidget):
    preview_clicked = pyqtSignal(str)
    checkbox_toggled = pyqtSignal(str, bool)

    def __init__(self, file_path, change_type):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Create and style the checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                border: 2px solid white;
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:checked {
                background-color: white;
            }
        """)
        self.checkbox.toggled.connect(lambda state: self.checkbox_toggled.emit(file_path, state))
        layout.addWidget(self.checkbox)

        label = QLabel(f"{change_type}: {file_path}")
        layout.addWidget(label)

        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(lambda: self.preview_clicked.emit(file_path))
        layout.addWidget(preview_button)

class FileChangesList(QListWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setVisible(False)

    def show_file_changes(self, processor):
        self.clear()
        self.parent.logic.file_changes.clear()
        for file in processor.response["files"]:
            self.add_file_change_widget(file["path"], file["action"])
        self.setVisible(True)

    def add_file_change_widget(self, file_path, change_type):
        widget = FileChangeWidget(file_path, change_type)
        widget.preview_clicked.connect(self.parent.show_file_preview)
        widget.checkbox_toggled.connect(self.parent.toggle_file_change)
        
        item = QListWidgetItem(self)
        item.setSizeHint(widget.sizeHint())
        
        self.addItem(item)
        self.setItemWidget(item, widget)
        
        self.parent.logic.file_changes[file_path] = change_type

    def toggle_file_change(self, file_path, state):
        # This method should be implemented in the parent class to handle checkbox state changes
        pass
