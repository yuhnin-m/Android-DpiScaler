import sys
import logging
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs.txt", mode='a', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
handler.setFormatter(formatter)

logger.handlers = [handler]


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
