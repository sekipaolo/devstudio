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

    def get_file_preview_content(self, file_path: str, change_type: str) -> str:
        self.logger.debug("Getting file preview content for %s (change type: %s)", file_path, change_type)
        if change_type == "create" or change_type == "update":
            full_path = os.path.join(self.ai_interaction.tmp_dir, file_path)
            self.logger.debug("Reading file from temporary directory: %s", full_path)
            with open(full_path, 'r') as file:
                content = file.read()
        elif change_type == "delete":
            self.logger.debug("File marked for deletion: %s", file_path)
            content = "This file has been marked for deletion."
        else:
            full_path = os.path.join(self.project_folder, file_path)
            self.logger.debug("Reading file from project directory: %s", full_path)
            with open(full_path, 'r') as file:
                content = file.read()
        self.logger.debug("File preview content length: %d", len(content))
        return content

    def apply_file_changes(self):
        self.logger.debug("Applying file changes")
        for file_path, change_type in self.file_changes.items():
            self.logger.debug("Processing file: %s (change type: %s)", file_path, change_type)
            if change_type == "create" or change_type == "update":
                src_path = os.path.join(self.ai_interaction.tmp_dir, file_path)
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
