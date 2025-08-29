import logging
import os
import sys

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def get_app_data_dir():
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/PNG2Drawable")
    elif sys.platform == "win32":
        return os.path.join(os.getenv("APPDATA"), "PNG2Drawable")
    else:
        return os.path.expanduser("~/.png2drawable")


def setup_logging(log_path):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    except Exception as e:
        # fallback в /tmp если что-то пошло не так
        fallback_log = "/tmp/png2drawable_fallback.log"
        handler = logging.FileHandler(fallback_log, mode='a', encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - FATAL - %(message)s'))
        logger.addHandler(handler)
        logger.critical(f"Ошибка при создании лог-файла: {e}")
        return

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.handlers = [handler]


def main():
    app_data_dir = get_app_data_dir()
    os.makedirs(app_data_dir, exist_ok=True)

    log_path = os.path.join(app_data_dir, "logs.txt")
    setup_logging(log_path)

    logging.info("Application started")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
