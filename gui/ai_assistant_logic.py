import os
import logging
from typing import List, Dict, Optional
from ai import AIInteraction
from config.global_config import config
from ai.git_utils import create_git_commit
class AIAssistantLogic:
    def __init__(self, ):
        self.ai_interaction: AIInteraction = AIInteraction()
        self.file_changes: Dict[str, str] = {}
        
        # Set up logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def process_prompt(self, prompt: str, selected_files: List[Dict[str, str]]):
        result = self.ai_interaction.process_prompt(prompt, selected_files)
        return result

    def apply_file_changes(self):
        self.logger.debug("Applying file changes")
        for file_path, change_type in self.file_changes.items():
            self.logger.debug("Processing file: %s (change type: %s)", file_path, change_type)
            if change_type == "create" or change_type == "update":
                src_path = os.path.join(config.get("artifacts_dir"), file_path)
                dst_path = os.path.join(config.get("project_root"), file_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                with open(src_path, 'r') as src_file, open(dst_path, 'w') as dst_file:
                    content = src_file.read()
                    dst_file.write(content)
            elif change_type == "delete":
                file_to_delete = os.path.join(config.get("project_root"), file_path)
                os.remove(file_to_delete)
        
        self.logger.debug("All file changes applied, clearing file_changes dictionary")
        self.file_changes.clear()
        create_git_commit()
        self.logger.debug("created git commit")

    def get_file_preview_content(self, file_path: str, change_type: str) -> str:
        if change_type in ["create", "update"]:
            preview_path = os.path.join(config.get("artifacts_dir"), file_path)
        elif change_type == "delete":
            preview_path = os.path.join(config.get("project_root"), file_path)
        else:
            raise ValueError(f"Invalid change type: {change_type}")

        with open(preview_path, 'r') as file:
            return file.read()
