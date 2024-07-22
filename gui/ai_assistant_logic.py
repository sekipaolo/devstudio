import os
import logging
from typing import List, Dict, Optional
from ai import AIInteraction
from config.global_config import config
from ai.git_utils import create_git_commit
import shutil
class AIAssistantLogic:
    def __init__(self, ):
        self.ai_interaction: AIInteraction = AIInteraction()
        self.file_changes: Dict[str, str] = {}
        
        # Set up logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def process_prompt(self, prompt: str, selected_files: List[Dict[str, str]]):
        result = self.ai_interaction.process_prompt(prompt, selected_files)
        return result

    def apply_file_changes(self):
        self.logger.debug("Applying file changes")

        artifacts_dir = config.get("artifacts_dir")
        project_root = config.get("project_root")

        # Copy all files from artifacts_dir to project_root
        for root, _, files in os.walk(artifacts_dir):
            for file in files:
                if file == "deletions.txt":
                    continue
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, artifacts_dir)
                dst_path = os.path.join(project_root, rel_path)

                self.logger.debug(f"Copying file: {rel_path}")
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)

        # Delete files listed in deletions.txt
        deletions_file = os.path.join(artifacts_dir, "deletions.txt")
        if os.path.exists(deletions_file):
            with open(deletions_file, 'r') as f:
                for line in f:
                    file_to_delete = line.strip()
                    if file_to_delete:
                        file_path = os.path.join(project_root, file_to_delete)
                        if os.path.exists(file_path):
                            self.logger.debug(f"Deleting file: {file_to_delete}")
                            os.remove(file_path)
                        else:
                            self.logger.warning(f"File not found for deletion: {file_to_delete}")

        self.logger.debug("All file changes applied")
        create_git_commit()
        self.logger.debug("Created git commit")

    def get_file_preview_content(self, file_path: str, change_type: str) -> str:
        if change_type in ["create", "replace"]:
            preview_path = os.path.join(config.get("artifacts_dir"), file_path)
        elif change_type == "delete":
            preview_path = os.path.join(config.get("project_root"), file_path)
        else:
            raise ValueError(f"Invalid change type: {change_type}")

        with open(preview_path, 'r') as file:
            return file.read()
