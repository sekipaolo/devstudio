import os
from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from config.global_config import config

class ProjectManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def change_project_root(self):
        new_root = QFileDialog.getExistingDirectory(self.main_window, "Select Project Root Directory")
        if new_root:
            try:
                config.set("project_root", new_root)
                self.main_window.populate_file_tree()
                self.main_window.logging_manager.log('info', f"Project root changed to: {new_root}")
                QMessageBox.information(self.main_window, "Project Root Changed", f"Project root has been changed to:\n{new_root}")
            except Exception as e:
                self.main_window.logging_manager.log('error', f"Error changing project root: {str(e)}")
                QMessageBox.critical(self.main_window, "Error", f"Failed to change project root: {str(e)}")

    def on_item_clicked(self, index):
        # This method is now handled in the FileTreeView class
        pass

    def on_item_double_clicked(self, index):
        item = self.main_window.file_tree.model().itemFromIndex(index)
        if item.is_dir:  # It's a directory
            return
        
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self.main_window, 'Rename File', 'Enter new file name:', text=old_name)
        
        if ok and new_name and new_name != old_name:
            item.setText(new_name)
            self.main_window.prompt_input.append(f"\nPlease rename the file '{old_name}' to '{new_name}'.")

    def populate_file_tree(self):
        self.main_window.logging_manager.log('debug', "Populating file tree")
        try:
            model = self.main_window.file_tree.model()
            if model:
                model.clear()
                root = model.invisibleRootItem()
                self._populate_tree_recursive(config.get("project_root"), root)
                self.main_window.logging_manager.log('debug', f"File tree populated with {model.rowCount()} root items")
            else:
                raise ValueError("File tree model is not initialized")
        except Exception as e:
            self.main_window.logging_manager.log('error', f"Error populating file tree: {str(e)}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to populate file tree: {str(e)}")

    def _populate_tree_recursive(self, directory, parent):
        try:
            for name in sorted(os.listdir(directory)):
                if name in ['.git', '__pycache__']:
                    continue
                path = os.path.join(directory, name)
                if os.path.isdir(path):
                    folder = self.main_window.file_tree.FileTreeItem(name, is_dir=True)
                    parent.appendRow(folder)
                    self._populate_tree_recursive(path, folder)
                else:
                    item = self.main_window.file_tree.FileTreeItem(name)
                    parent.appendRow(item)
        except Exception as e:
            self.main_window.logging_manager.log('error', f"Error populating directory {directory}: {str(e)}")
