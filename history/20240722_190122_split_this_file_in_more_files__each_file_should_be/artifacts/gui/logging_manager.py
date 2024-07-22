import logging
from PyQt6.QtCore import Qt

class LoggingManager:
    def __init__(self):
        self.logger = logging.getLogger('GUI')
        self.setup_logging()
        self.logging_enabled = True

    def setup_logging(self):
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def toggle_logging(self, state):
        self.logging_enabled = state == Qt.CheckState.Checked.value
        if self.logging_enabled:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.CRITICAL)

    def log(self, level, message):
        if self.logging_enabled:
            if level == 'debug':
                self.logger.debug(message)
            elif level == 'info':
                self.logger.info(message)
            elif level == 'warning':
                self.logger.warning(message)
            elif level == 'error':
                self.logger.error(message)
            elif level == 'critical':
                self.logger.critical(message)
