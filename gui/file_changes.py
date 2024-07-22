from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import pyqtSignal

class FileChangeWidget(QWidget):
    preview_clicked = pyqtSignal(str)

    def __init__(self, file_path, change_type):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

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
        
        item = QListWidgetItem(self)
        item.setSizeHint(widget.sizeHint())
        
        self.addItem(item)
        self.setItemWidget(item, widget)
        
        self.parent.logic.file_changes[file_path] = change_type
