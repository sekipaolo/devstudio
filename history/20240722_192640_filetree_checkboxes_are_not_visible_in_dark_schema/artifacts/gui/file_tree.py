import os
from PyQt6.QtWidgets import QTreeView, QStyle, QProxyStyle
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPalette
from PyQt6.QtCore import Qt
from typing import List, Dict

class CheckboxStyle(QProxyStyle):
    def subElementRect(self, element, option, widget=None):
        r = super().subElementRect(element, option, widget)
        if element == QStyle.SubElement.SE_ItemViewItemCheckIndicator:
            r.moveCenter(option.rect.center())
        return r

class FileTreeView(QTreeView):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.clicked.connect(self.on_item_clicked)
        self.doubleClicked.connect(self.on_item_double_clicked)
        
        # Apply custom style to make checkboxes visible in dark mode
        self.setStyle(CheckboxStyle(self.style()))

    def populate(self, root_path):
        self.model.clear()
        root_item = self.model.invisibleRootItem()
        self._populate_recursive(root_path, root_item)

    def _populate_recursive(self, directory: str, parent: QStandardItem):
        for name in sorted(os.listdir(directory)):
            if name in ['.git', '__pycache__']:
                continue
            path = os.path.join(directory, name)
            item = QStandardItem(name)
            item.setCheckable(True)
            item.setData(path, Qt.ItemDataRole.UserRole)
            parent.appendRow(item)
            if os.path.isdir(path):
                item.setData(True, Qt.ItemDataRole.UserRole + 1)  # Store is_dir information
                self._populate_recursive(path, item)
            else:
                item.setData(False, Qt.ItemDataRole.UserRole + 1)

    def on_item_clicked(self, index):
        item = self.model.itemFromIndex(index)
        item.setCheckState(Qt.CheckState.Checked if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked)

    def on_item_double_clicked(self, index):
        item = self.model.itemFromIndex(index)
        if not item.data(Qt.ItemDataRole.UserRole + 1):  # Not a directory
            # Implement rename functionality here
            pass

    def get_selected_files(self) -> List[Dict[str, str]]:
        selected_files = []
        def traverse(parent: QStandardItem):
            for row in range(parent.rowCount()):
                child = parent.child(row)
                if child.checkState() == Qt.CheckState.Checked and not child.data(Qt.ItemDataRole.UserRole + 1):
                    file_path = child.data(Qt.ItemDataRole.UserRole)
                    try:
                        with open(file_path, 'r') as file:
                            content = file.read()
                        selected_files.append({"path": file_path, "content": content})
                    except Exception as e:
                        print(f"Error reading file {file_path}: {str(e)}")
                if child.hasChildren():
                    traverse(child)
        
        root = self.model.invisibleRootItem()
        traverse(root)
        return selected_files

    def get_file_path(self, item: QStandardItem) -> str:
        path = []
        while item is not None:
            path.append(item.text())
            item = item.parent()
        return os.path.join(*reversed(path[:-1]))  # Exclude the invisible root item
