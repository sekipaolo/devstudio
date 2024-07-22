import logging
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtCore import Qt

def setup_logging():
    logger = logging.getLogger('GUI')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

class LoggingToggle(QCheckBox):
    def __init__(self, logger):
        super().__init__("Enable GUI Logging")
        self.logger = logger
        self.setChecked(True)
        self.stateChanged.connect(self.toggle_logging)

    def toggle_logging(self, state):
        if state == Qt.CheckState.Checked.value:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.CRITICAL)
