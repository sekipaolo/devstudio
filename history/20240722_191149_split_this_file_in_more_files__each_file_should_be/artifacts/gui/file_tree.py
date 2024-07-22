import os
from PyQt6.QtWidgets import QTreeView
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtCore import Qt
from typing import List, Dict

class FileTreeItem:
    def __init__(self, name, is_dir=False):
        self.name = name
        self.is_dir = is_dir
        self.children = []
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

class FileTreeView(QTreeView):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.clicked.connect(self.on_item_clicked)
        self.doubleClicked.connect(self.on_item_double_clicked)

    def populate(self, root_path):
        self.model.clear()
        root_item = self.model.invisibleRootItem()
        self._populate_recursive(root_path, root_item)

    def _populate_recursive(self, directory: str, parent: FileTreeItem):
        for name in sorted(os.listdir(directory)):
            if name in ['.git', '__pycache__']:
                continue
            path = os.path.join(directory, name)
            if os.path.isdir(path):
                folder = FileTreeItem(name, is_dir=True)
                parent.add_child(folder)
                self._populate_recursive(path, folder)
            else:
                item = FileTreeItem(name)
                parent.add_child(item)

    def on_item_clicked(self, index):
        item = self.model.itemFromIndex(index)
        item.setCheckState(Qt.CheckState.Checked if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked)

    def on_item_double_clicked(self, index):
        item = self.model.itemFromIndex(index)
        if not item.is_dir:
            # Implement rename functionality here
            pass

    def get_selected_files(self) -> List[Dict[str, str]]:
        selected_files = []
        def traverse(parent: FileTreeItem):
            for child in parent.children:
                if child.checkState() == Qt.CheckState.Checked and not child.is_dir:
                    file_path = self.get_file_path(child)
                    try:
                        with open(file_path, 'r') as file:
                            content = file.read()
                        selected_files.append({"path": file_path, "content": content})
                    except Exception as e:
                        print(f"Error reading file {file_path}: {str(e)}")
                if child.children:
                    traverse(child)
        
        root = self.model.invisibleRootItem()
        traverse(root)
        return selected_files

    def get_file_path(self, item: FileTreeItem) -> str:
        path = []
        while item is not None:
            path.append(item.name)
            item = item.parent
        return os.path.join(*reversed(path))
