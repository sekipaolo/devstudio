import os

import re
import logging
from .xml_parser import XMLParser
from config.global_config import config
class ResponseProcessor:
    def __init__(self, ):

        self.response = {}
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.xml_parser = XMLParser()

    def process_response(self, response):
        self.logger.debug("Processing response")
        self.response = {"text": [], "files": []}
        # Extract XML content
        xml_match = re.search(r'<response>.*</response>', response, re.DOTALL)
        if xml_match:
            xml_content = xml_match.group(0)
            # Extract free text before and after XML
            self.response['text'] += re.split(r'<response>.*</response>', response, flags=re.DOTALL)
            self.logger.debug("XML content extracted successfully")
        else:
            self.logger.error("No XML content found in the response")
            return

        parsed_xml = self.xml_parser.parse_xml(xml_content)
        if parsed_xml is None:
            self.logger.error("Failed to parse XML content")
            return

        self.response['text'] += self.xml_parser.extract_text(parsed_xml)
        file_changes = self.xml_parser.extract_file_changes(parsed_xml)
        self.logger.debug(f"Extracted {len(file_changes)} file changes")

        for file_change in file_changes:
            for file_info in file_change['files']:
                processed_file = self.process_file(file_info)
                processed_file['explanations'] = file_change['explanations']
                self.response['files'].append(processed_file)

        self.logger.debug("Response processing completed")

    def process_file(self, file_info):
        file_path = file_info['path']
        action = file_info['action']
        original_path = os.path.join(config.get("project_root"), file_path)
        tmp_path = os.path.join(config.get("artifacts_dir"), file_path)

        self.logger.debug(f"Processing file: {file_path} with action: {action}")
        if action == 'delete':
            if os.path.exists(original_path):
                self.logger.info(f"Marked file for deletion: {file_path}")
                with open(os.path.join(config.get("artifacts_dir"), 'deletions.txt'), 'w') as f:
                    f.write(file_path + "\n")
            else:
                self.logger.warning(f"Attempted to delete non-existent file: {file_path}")
            return file_info

        new_content = file_info['content'] + '\n' if file_info['content'] else ''
        file_info['content'] = new_content

        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
        with open(tmp_path, 'w') as f:
            f.write(new_content)
        self.logger.debug(f"Wrote content to temporary file: {tmp_path}")

        if action == 'create' or not os.path.exists(original_path):
            self.logger.info(f"Created new file: {file_path}")
        else:
            with open(original_path, 'r') as f:
                original_content = f.read()
            
            if original_content.strip() != new_content.strip():
                self.logger.info(f"Updated file: {file_path}")
            else:
                self.logger.info(f"No changes in file: {file_path}")

        return file_info