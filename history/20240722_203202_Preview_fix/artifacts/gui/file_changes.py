from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import pyqtSignal

class FileChangeWidget(QWidget):
    preview_clicked = pyqtSignal(str, str)

    def __init__(self, file_path, change_type, content):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.file_path = file_path
        self.content = content

        label = QLabel(f"{change_type}: {file_path}")
        layout.addWidget(label)

        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(self.emit_preview_clicked)
        layout.addWidget(preview_button)

    def emit_preview_clicked(self):
        self.preview_clicked.emit(self.file_path, self.content)

class FileChangesList(QListWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setVisible(False)

    def show_file_changes(self, processor):
        self.clear()
        self.parent.logic.file_changes.clear()
        for file in processor.response["files"]:
            self.add_file_change_widget(file["path"], file["action"], file.get("content", ""))
        self.setVisible(True)

    def add_file_change_widget(self, file_path, change_type, content):
        widget = FileChangeWidget(file_path, change_type, content)
        widget.preview_clicked.connect(self.parent.show_file_preview)
        
        item = QListWidgetItem(self)
        item.setSizeHint(widget.sizeHint())
        
        self.addItem(item)
        self.setItemWidget(item, widget)
        
        self.parent.logic.file_changes[file_path] = change_type
