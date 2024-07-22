import os
import subprocess
from PyQt6.QtWidgets import QPushButton, QFileDialog, QMessageBox
from config.global_config import config

class ProjectRootManager:
    def __init__(self, parent):
        self.parent = parent
        self.change_root_button = QPushButton("Change Project Root")
        self.change_root_button.clicked.connect(self.change_project_root)

    def change_project_root(self):
        new_root = QFileDialog.getExistingDirectory(self.parent, "Select Project Root Directory")
        if new_root:
            try:
                config.set("project_root", new_root)
                self.parent.populate_file_tree()
                self.parent.logger.info(f"Project root changed to: {new_root}")
                QMessageBox.information(self.parent, "Project Root Changed", f"Project root has been changed to:\n{new_root}")
            except Exception as e:
                self.parent.logger.error(f"Error changing project root: {str(e)}")
                QMessageBox.critical(self.parent, "Error", f"Failed to change project root: {str(e)}")

    def get_latest_commit(self):
        try:
            result = subprocess.run(['git', 'log', '-1', '--oneline'], 
                                    cwd=config.get("project_root"),
                                    capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.parent.logger.error(f"Error getting latest git commit: {str(e)}")
            return "Unable to retrieve latest commit"

    def show_latest_commit(self):
        commit = self.get_latest_commit()
        QMessageBox.information(self.parent, "Latest Git Commit", f"Latest commit:\n{commit}")
