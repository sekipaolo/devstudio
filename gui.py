import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit, QLabel, QFileDialog, QComboBox
from PyQt6.QtCore import Qt

# Import your LocalAIAgent class from the renamed file
from agent import LocalAIAgent

class AIAgentGUI(QMainWindow):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.initUI()

    def initUI(self):
        self.setWindowTitle('AI Developer Assistant')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Project selection
        project_layout = QHBoxLayout()
        self.project_path = QLineEdit(self.agent.project_path)
        project_layout.addWidget(QLabel('Project Path:'))
        project_layout.addWidget(self.project_path)
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_project)
        project_layout.addWidget(browse_button)
        layout.addLayout(project_layout)

        # LLM selection
        llm_layout = QHBoxLayout()
        llm_layout.addWidget(QLabel('Select LLM:'))
        self.llm_dropdown = QComboBox()
        self.llm_dropdown.addItems(['Claude', 'ChatGPT'])
        self.llm_dropdown.setCurrentText('Claude')  # Set Claude as default
        llm_layout.addWidget(self.llm_dropdown)
        layout.addLayout(llm_layout)

        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)

        # User input
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        input_layout.addWidget(self.user_input)
        send_button = QPushButton('Send')
        send_button.clicked.connect(self.send_request)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)

        # Status bar
        self.statusBar().showMessage('Ready')

    def browse_project(self):
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        if folder_path:  # Only update if a folder was selected
            self.project_path.setText(folder_path)
            self.agent.set_project_path(folder_path)
            self.statusBar().showMessage(f'Project set to: {folder_path}')

    def send_request(self):
        user_input = self.user_input.text()
        self.chat_history.append(f"You: {user_input}")
        self.user_input.clear()

        # Get the selected LLM
        selected_llm = self.llm_dropdown.currentText()
        use_claude = (selected_llm == 'Claude')        
        response = self.agent.process_request(user_input, use_claude)
        self.chat_history.append(f"AI ({selected_llm}): {response}")
        self.statusBar().showMessage('Request processed')

def run_gui():
    # Load environment variables
    load_dotenv()

    # Get API keys from environment variables
    openai_api_key = os.getenv('OPENAI_API_KEY')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

    if not openai_api_key or not anthropic_api_key:
        print("Error: API keys not found in .env file")
        sys.exit(1)

    # Get the directory where the script is run
    current_dir = os.getcwd()

    # Create the agent with API keys and current directory as default project path
    agent = LocalAIAgent(current_dir, openai_api_key, anthropic_api_key)

    app = QApplication(sys.argv)
    ex = AIAgentGUI(agent)
    ex.show()
    sys.exit(app.exec())

# Usage
if __name__ == '__main__':
    run_gui()