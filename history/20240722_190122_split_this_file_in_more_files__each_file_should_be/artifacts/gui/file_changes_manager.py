from PyQt6.QtWidgets import QListWidgetItem, QMessageBox
from .widgets import FileChangeWidget
from .file_preview_popup import FilePreviewPopup
import subprocess

class FileChangesManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def show_file_changes(self, processor):
        self.main_window.file_changes_list.clear()
        self.main_window.logic.file_changes.clear()
        for file in processor.response["files"]:
            self.add_file_change_widget(file["path"], file["action"])
        self.main_window.file_changes_list.setVisible(True)

    def add_file_change_widget(self, file_path, change_type):
        widget = FileChangeWidget(file_path, change_type)
        widget.preview_clicked.connect(self.show_file_preview)
        
        item = QListWidgetItem(self.main_window.file_changes_list)
        item.setSizeHint(widget.sizeHint())
        
        self.main_window.file_changes_list.addItem(item)
        self.main_window.file_changes_list.setItemWidget(item, widget)
        
        self.main_window.logic.file_changes[file_path] = change_type

    def show_file_preview(self, file_path):
        change_type = self.main_window.logic.file_changes.get(file_path)

        try:
            content = self.main_window.logic.get_file_preview_content(file_path, change_type)
            popup = FilePreviewPopup(file_path, content)
            popup.exec()
        except Exception as e:
            self.main_window.logging_manager.log('error', f"Error showing file preview for {file_path}: {str(e)}")
            QMessageBox.warning(self.main_window, "Preview Error", f"Failed to show preview for {file_path}: {str(e)}")

    def apply_file_changes(self):
        try:
            self.main_window.logic.apply_file_changes()
            self.main_window.project_manager.populate_file_tree()  # Refresh the file tree
            self.main_window.file_changes_list.clear()
            self.main_window.apply_changes_button.setVisible(False)  # Hide the button after changes are applied
            QMessageBox.information(self.main_window, "Response processed", "All file changes have been saved successfully.")
            
            # Show the latest git commit
            self.show_latest_commit()
        except Exception as e:
            self.main_window.logging_manager.log('error', f"Error applying file changes: {str(e)}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to apply file changes: {str(e)}")

    def get_latest_commit(self):
        try:
            result = subprocess.run(['git', 'log', '-1', '--oneline'], 
                                    cwd=self.main_window.project_manager.config.get("project_root"),
                                    capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.main_window.logging_manager.log('error', f"Error getting latest git commit: {str(e)}")
            return "Unable to retrieve latest commit"

    def show_latest_commit(self):
        commit = self.get_latest_commit()
        QMessageBox.information(self.main_window, "Latest Git Commit", f"Latest commit:\n{commit}")
