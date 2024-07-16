import os
import logging
from typing import List, Dict, Optional
from ai import AIInteraction

class AIAssistantLogic:
    def __init__(self, project_folder: str):
        self.project_folder: str = project_folder
        self.ai_interaction: AIInteraction = AIInteraction(self.project_folder)
        self.file_changes: Dict[str, str] = {}
        
        # Set up logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.debug("AIAssistantLogic initialized with project folder: %s", self.project_folder)

    def process_prompt(self, prompt: str, selected_files: List[Dict[str, str]]):
        self.logger.debug("Processing prompt: %s", prompt)
        self.logger.debug("Selected files: %s", selected_files)
        result = self.ai_interaction.process_prompt(prompt, selected_files)
        return result

    def apply_file_changes(self):
        self.logger.debug("Applying file changes")
        for file_path, change_type in self.file_changes.items():
            self.logger.debug("Processing file: %s (change type: %s)", file_path, change_type)
            if change_type == "create" or change_type == "update":
                src_path = os.path.join(self.ai_interaction.artifacts_dir, file_path)
                dst_path = os.path.join(self.project_folder, file_path)
                self.logger.debug(f"{change_type}ing {dst_path}")
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                with open(src_path, 'r') as src_file, open(dst_path, 'w') as dst_file:
                    content = src_file.read()
                    dst_file.write(content)
                self.logger.debug("File created/updated successfully: %s", dst_path)
            elif change_type == "delete":
                file_to_delete = os.path.join(self.project_folder, file_path)
                self.logger.debug("Deleting file: %s", file_to_delete)
                os.remove(file_to_delete)
                self.logger.debug("File deleted successfully: %s", file_to_delete)
        
        self.logger.debug("All file changes applied, clearing file_changes dictionary")
        self.file_changes.clear()

    def change_project_folder(self, new_project_folder: str):
        self.logger.debug(f"Changing project folder to: {new_project_folder}")
        if not os.path.isdir(new_project_folder):
            raise ValueError(f"The specified path is not a valid directory: {new_project_folder}")
        
        self.project_folder = new_project_folder
        self.ai_interaction = AIInteraction(self.project_folder)
        self.file_changes.clear()
        self.logger.debug(f"Project folder changed successfully to: {self.project_folder}")

    def get_file_preview_content(self, file_path: str, change_type: str) -> str:
        if change_type in ["create", "update"]:
            preview_path = os.path.join(self.ai_interaction.artifacts_dir, file_path)
        elif change_type == "delete":
            preview_path = os.path.join(self.project_folder, file_path)
        else:
            raise ValueError(f"Invalid change type: {change_type}")

        with open(preview_path, 'r') as file:
            return file.read()
