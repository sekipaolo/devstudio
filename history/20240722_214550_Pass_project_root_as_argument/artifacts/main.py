import sys
import os
from PyQt6.QtWidgets import QApplication
from gui import AIAssistantGUI

def main():
    app = QApplication(sys.argv)
    
    # Check if a project root argument is provided
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        # Use the current directory as default if no argument is provided
        project_root = os.getcwd()
    
    # Ensure the project root is an absolute path
    project_root = os.path.abspath(project_root)
    
    # Create the GUI instance with the specified project root
    ex = AIAssistantGUI(project_root)
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
