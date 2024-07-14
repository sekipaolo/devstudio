import datetime
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from .response_processor import ResponseProcessor
from .prompt_processor import PromptProcessor
from .git_utils import create_git_commit

load_dotenv()
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AIInteraction:
    def __init__(self, project_root):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.project_root = project_root
        self.selected_files = None
        self.prompt_processor = PromptProcessor(project_root)
        logger.debug(f"AIInteraction initialized with project root: {project_root}")

    def process_prompt(self, prompt, selected_files):
        logger.debug("Processing prompt")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.history_dir = os.path.join('history', timestamp)
        self.artifacts_dir = os.path.join(self.history_dir, 'artifacts')
        os.makedirs(self.history_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)
        logger.debug(f"Created history directory: {self.history_dir}")

        formatted_prompt = self._prepare_prompt(prompt, selected_files)
        self._save_prompt(formatted_prompt)

        logger.debug("Sending request to Anthropic API")
        raw_response = self._send_request_to_anthropic(formatted_prompt)
        logger.debug("Received response from Anthropic API")

        response = raw_response.content[0].text
        self._save_response(response)

        processor = ResponseProcessor(self.project_root, self.artifacts_dir)
        processor.process_response(response)
        logger.debug("Processed response")
            
        create_git_commit(self.project_root, self.history_dir)
        logger.info("Response processed and git commit created. Please check the 'history' directory for the saved chat and artifacts.")
        return response, processor

    def _prepare_prompt(self, prompt, selected_files):
        return self.prompt_processor.prepare_prompt(prompt, selected_files)

    def _save_prompt(self, formatted_prompt):
        with open(os.path.join(self.history_dir, 'prompt.xml'), 'w') as f:
            f.write(formatted_prompt)
        logger.debug("Saved prompt to history")

    def _send_request_to_anthropic(self, formatted_prompt):
        return self.anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": formatted_prompt}
            ]
        )

    def _save_response(self, response):
        with open(os.path.join(self.history_dir, 'response.xml'), 'w') as f:
            f.write(response)
        logger.debug("Saved response to history")