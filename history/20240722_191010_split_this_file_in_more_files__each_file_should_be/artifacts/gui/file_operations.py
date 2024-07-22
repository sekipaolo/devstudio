import os
from PyQt6.QtWidgets import QMessageBox, QInputDialog
from PyQt6.QtCore import Qt
from .file_tree import FileTreeItem
from config.global_config import config

class FileOperationsMixin:
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

    def on_item_double_clicked(self, index):
        item = self.file_tree.model().itemFromIndex(index)
        if item.is_dir:
            return
        
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, 'Rename File', 'Enter new file name:', text=old_name)
        
        if ok and new_name and new_name != old_name:
            item.setText(new_name)
            self.prompt_input.append(f"\nPlease rename the file '{old_name}' to '{new_name}'.")

    def get_selected_files(self):
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

    def get_file_path(self, item: FileTreeItem):
        path = []
        while item is not None:
            path.append(item.text())
            item = item.parent()
        return os.path.join(config.get("project_root"), *reversed(path))
