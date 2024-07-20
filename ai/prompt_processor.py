import os
import mimetypes
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
from config.global_config import config
class PromptProcessor:
    def __init__(self):
        pass

    def prepare_prompt(self, prompt, selected_files):
        logger.debug("Preparing prompt")
        guidelines_text = """
            Format your answer as an XML document as this example. Remember to escape XML tags characters (< and >) characters:
           <response>
               <text>Any text not related to file changes</text>
               <file-changes>
                   <file path="gui/widgets.py" action="replace">
                        Here the full runnable content of the file
                   </file>
                   <file path="gui/new_file.py" action="create">
                        Here the full content of the newly created file
                   </file>
                   <file path="gui/deleted_file.py" action="delete"/>
                   <explanation>
                        Here the explanation of the changes
                   </explanation>                    
               </file-changes>
           </response>
        """

        sources_text = ""
        for file in selected_files:
            relative_path = os.path.relpath(file['path'], start=config.get("project_root"))
            file_type, _ = mimetypes.guess_type(file['path'])
            if file_type is None:
                file_type = "application/octet-stream"
            
            sources_text += (
                f"<Source path=\"{relative_path}\">\n"
                f"{file['content']}\n"
                "</Source>\n"
            )
            logger.debug(f"Added source file: {relative_path}")

        formatted_prompt = (
            f"<Guidelines>{guidelines_text}</Guidelines>"
            f"<Sources>{sources_text}</Sources>"        
            f"<Task>{prompt}</Task>\n\n" 
        ).replace("<", "&lt;").replace(">", "&gt;")
        logger.debug("Prompt prepared successfully")
        return formatted_prompt