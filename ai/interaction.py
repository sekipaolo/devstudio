import datetime
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from .response_processor import ResponseProcessor
from .prompt_processor import PromptProcessor


load_dotenv()
import logging
from config.global_config import config
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AIInteraction:
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.selected_files = None
        self.prompt_processor = PromptProcessor()

    def process_prompt(self, prompt, selected_files):
        logger.debug("Processing prompt")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if(not config.get("change_name")):
            config.set("change_name", self._generate_summary(prompt))
        config.set("history_dir", os.path.join(
            config.get("project_root"), 
            'history', timestamp + "_" + config.get("change_name")))
        config.set("artifacts_dir", os.path.join(config.get("history_dir"), 'artifacts'))
        os.makedirs(config.get("history_dir"), exist_ok=True)
        os.makedirs(config.get("artifacts_dir"), exist_ok=True)

        formatted_prompt = self._prepare_prompt(prompt, selected_files)
        self._save_prompt(formatted_prompt)

        logger.debug("Sending request to Anthropic API")
        raw_response = self._send_request_to_anthropic(formatted_prompt)
        logger.debug("Received response from Anthropic API")

        response = raw_response.content[0].text
        self._save_response(response)

        processor = ResponseProcessor()
        processor.process_response(response)
        logger.debug("Processed response")
            
        logger.info("Response processed and git commit created. Please check the 'history' directory for the saved chat and artifacts.")
        return response, processor

    def _prepare_prompt(self, prompt, selected_files):
        return self.prompt_processor.prepare_prompt(prompt, selected_files)

    def _save_prompt(self, formatted_prompt):
        with open(os.path.join(config.get("history_dir"), 'prompt.xml'), 'w') as f:
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
        with open(os.path.join(config.get("history_dir"), 'response.xml'), 'w') as f:
            f.write(response)
        logger.debug("Saved response to history")

    def _generate_summary(self, prompt):
        words = prompt.split()
        summary = '_'.join(words[:10])  # Take the first 10 words
        summary = summary.lower()  # Convert to lowercase
        summary = ''.join(c if c.isalnum() or c == '_' else '_' for c in summary)  # Replace non-alphanumeric chars with underscore
        summary = summary[:50]  # Limit to 50 characters
        return summary
