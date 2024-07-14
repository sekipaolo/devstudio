import xml.etree.ElementTree as ET
import logging
import re

class XMLParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("XMLParser initialized")

    def parse_xml(self, xml_content):
        self.logger.debug("Parsing XML content")
        try:
            root = ET.fromstring(xml_content)
            parsed_result = self._process_element(root)
            self.logger.debug("XML parsing successful")
            return parsed_result
        except ET.ParseError as e:
            self.logger.error(f"Error parsing XML: {e}")
            return None

    def _process_element(self, element):
        self.logger.debug(f"Processing element: {element.tag}")
        result = {
            'tag': element.tag,
            'attributes': element.attrib,
            'text': element.text.strip() if element.text else None,
            'children': []
        }

        for child in element:
            result['children'].append(self._process_element(child))

        return result

    def extract_text(self, parsed_xml):
        self.logger.debug("Extracting text from parsed XML")
        texts = []
        self._extract_text_recursive(parsed_xml, texts)
        self.logger.debug(f"Extracted {len(texts)} text segments")
        return texts

    def _extract_text_recursive(self, element, texts):
        if element['tag'] == 'text' and element['text']:
            texts.append(element['text'] + ".\n\n")
            self.logger.debug(f"Extracted text: {element['text'][:50]}...")
        for child in element['children']:
            self._extract_text_recursive(child, texts)

    def extract_file_changes(self, parsed_xml):
        self.logger.debug("Extracting file changes from parsed XML")
        file_changes = []
        self._extract_file_changes_recursive(parsed_xml, file_changes)
        self.logger.debug(f"Extracted {len(file_changes)} file changes")
        return file_changes

    def _extract_file_changes_recursive(self, element, file_changes):
        if element['tag'] == 'file-changes':
            current_file_change = {'files': [], 'explanations': []}
            for child in element['children']:
                if child['tag'] == 'file':
                    file_info = {
                        'path': child['attributes'].get('path'),
                        'action': child['attributes'].get('action', 'update'),
                        'content': child['text']
                    }
                    current_file_change['files'].append(file_info)
                    self.logger.debug(f"Extracted file change: {file_info['path']} ({file_info['action']})")
                elif child['tag'] == 'explanation':
                    current_file_change['explanations'].append(child['text'])
                    self.logger.debug("Extracted explanation for file change")
            file_changes.append(current_file_change)
        else:
            for child in element['children']:
                self._extract_file_changes_recursive(child, file_changes)

    def process_response(self, response):
        self.logger.debug("Processing response")
        processed_content = []

        # Extract content before &lt;response&gt; tag
        pre_response = re.split(r'&lt;response&gt;', response, 1)[0].strip()
        if pre_response:
            processed_content.append(pre_response)

        # Parse the XML content
        xml_match = re.search(r'&lt;response&gt;.*&lt;/response&gt;', response, re.DOTALL)
        if xml_match:
            xml_content = xml_match.group(0)
            parsed_xml = self.parse_xml(xml_content)
            if parsed_xml:
                processed_content.extend(self.extract_text(parsed_xml))
                file_changes = self.extract_file_changes(parsed_xml)
                if file_changes:
                    processed_content.append("File Changes:")
                    for change in file_changes:
                        for file_info in change['files']:
                            action = file_info['action'].capitalize()
                            path = file_info['path']
                            processed_content.append(f"- {action}: {path}")
                        for explanation in change['explanations']:
                            processed_content.append("\nExplanation:")
                            processed_content.append(explanation)

        self.logger.debug("Response processing completed")
        return '\n\n'.join(processed_content)