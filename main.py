import sys
from PyQt6.QtWidgets import QApplication
from gui import AIAssistantGUI

def main():
    app = QApplication(sys.argv)
    ex = AIAssistantGUI()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()