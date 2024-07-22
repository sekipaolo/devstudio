import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from gui import AIAssistantGUI

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_modified = time.time()

    def on_modified(self, event):
        if event.src_path.endswith('.py') and 'history' not in event.src_path.split(os.path.sep):
            current_time = time.time()
            if current_time - self.last_modified > 1:  # Debounce mechanism
                self.last_modified = current_time
                print(f"File {event.src_path} has been modified. Restarting...")
                self.callback()

def watch_files(callback):
    observer = Observer()
    handler = ChangeHandler(callback)
    for root, dirs, files in os.walk('.'):
        if 'history' in dirs:
            dirs.remove('history')  # Don't traverse into 'history' directories
        observer.schedule(handler, path=root, recursive=False)
    observer.start()
    return observer

def restart_application():
    QApplication.quit()

def main():
    app = QApplication(sys.argv)
    ex = AIAssistantGUI()
    ex.show()

    # Set up file watcher
    observer = watch_files(restart_application)

    # Use a timer to process file system events
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # Dummy slot
    timer.start(500)  # Check every 500 ms

    exit_code = app.exec()

    # Clean up
    observer.stop()
    observer.join()

    if exit_code == 0:
        print("Application exited normally. Restarting...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        sys.exit(exit_code)

if __name__ == '__main__':
    main()