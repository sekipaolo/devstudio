import os
import git
import openai
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

class LocalAIAgent:
    def __init__(self, project_path):
        self.project_path = project_path
        self.init_git_repo()
        self.chat_history = []
        self.openai_client = openai.OpenAI()
        self.anthropic_client = Anthropic()
        
    def init_git_repo(self):
        try:
            self.repo = git.Repo(self.project_path)
        except git.exc.InvalidGitRepositoryError:
            self.repo = git.Repo.init(self.project_path)
            self.repo.git.add(A=True)
            self.repo.index.commit("Initial commit")
        
    def get_file_content(self, file_path):
        full_path = os.path.join(self.project_path, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as file:
                return file.read()
        return ""
        
    def update_file(self, file_path, content):
        full_path = os.path.join(self.project_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as file:
            file.write(content)
        
    def commit_changes(self, message):
        self.repo.git.add(A=True)
        self.repo.index.commit(message)
        
    def get_context(self):
        context = "Current project state:\n"
        for file in self.repo.git.ls_files().split('\n'):
            if file:  # Check if file is not an empty string
                context += f"File: {file}\nContent:\n{self.get_file_content(file)}\n\n"
        return context
    
    def call_llm(self, prompt, use_claude=False):
        if use_claude:
            response = self.anthropic_client.completions.create(
                model="claude-2.1",
                prompt=f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}",
                max_tokens_to_sample=1000,
            )
            return response.completion
        else:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
    
    def process_request(self, user_input):
        context = self.get_context()
        prompt = f"Context:\n{context}\n\nUser request: {user_input}\n\nPlease provide a complete solution, including full code snippets and file paths where they should be placed."
        
        response = self.call_llm(prompt)
        self.chat_history.append({"user": user_input, "ai": response})
        
        # Here you would parse the response and update files accordingly
        # For simplicity, let's assume the response includes file paths and content
        # You'd need to implement proper parsing based on the actual response format
        
        # Example (you'd need to adapt this based on actual response format):
        # updated_files = parse_response(response)
        # for file_path, content in updated_files.items():
        #     self.update_file(file_path, content)
        
        self.commit_changes(f"AI update based on: {user_input}")
        
        return response

# Usage
if __name__ == "__main__":
    agent = LocalAIAgent("/home/sekipaolo/apps/agi/devstudio")
    while True:
        user_input = input("Enter your request (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        response = agent.process_request(user_input)
        print(response)

    # Save chat history
    with open('chat_history.txt', 'w') as f:
        for entry in agent.chat_history:
            f.write(f"User: {entry['user']}\nAI: {entry['ai']}\n\n")