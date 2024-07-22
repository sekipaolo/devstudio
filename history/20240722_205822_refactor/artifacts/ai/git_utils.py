import os
import subprocess
import logging
import datetime
from config.global_config import config

logger = logging.getLogger(__name__)

def create_git_commit():
    try:
        # Change to the project root directory
        os.chdir(config.get("project_root"))

        # Add all changes in the project root
        subprocess.run(["git", "add", "."], check=True)

        # Add all files in the history directory
        subprocess.run(["git", "add", config.get("history_dir")], check=True)

        # Extract the summary from the history directory name
        summary = os.path.basename(config.get("change_name"))

        # Create a commit with a descriptive message including the summary
        commit_message = f"AI-assisted changes: {summary} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        logger.info(f"Created git commit: {commit_message}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating git commit: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during git commit: {e}")
    finally:
        # Change back to the original directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

def rollback_to_last_commit():
    try:
        # Check for uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], cwd=config.get("project_root"), capture_output=True, text=True)
        if result.stdout.strip():
            # There are uncommitted changes
            return "uncommitted_changes"

        # Rollback to the last commit
        subprocess.run(["git", "reset", "--hard", "HEAD~1"], cwd=config.get("project_root"), check=True)
        return "success"
    except subprocess.CalledProcessError as e:
        logger.error(f"Error rolling back to last commit: {str(e)}")
        return f"error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error during rollback: {str(e)}")
        return f"unexpected_error: {str(e)}"

def hard_reset():
    try:
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=config.get("project_root"), check=True)
        subprocess.run(["git", "clean", "-fd"], cwd=config.get("project_root"), check=True)
        return "success"
    except subprocess.CalledProcessError as e:
        logger.error(f"Error performing hard reset: {str(e)}")
        return f"error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error during hard reset: {str(e)}")
        return f"unexpected_error: {str(e)}"
