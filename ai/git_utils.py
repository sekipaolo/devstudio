import os
import subprocess
import logging
import datetime

logger = logging.getLogger(__name__)

def create_git_commit(project_root, history_dir):
    try:
        # Change to the project root directory
        os.chdir(project_root)

        # Add all changes in the project root
        subprocess.run(["git", "add", "."], check=True)

        # Add all files in the history directory
        subprocess.run(["git", "add", history_dir], check=True)

        # Create a commit with a descriptive message
        commit_message = f"AI-assisted changes - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        logger.info(f"Created git commit: {commit_message}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating git commit: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during git commit: {e}")
    finally:
        # Change back to the original directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
