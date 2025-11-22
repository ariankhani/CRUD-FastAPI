# logger.py
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_file, level=None, log_dir='logs') -> logging.Logger:
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, log_file)
    if level is None:
        level = logging.DEBUG if os.getenv("ENV") == "development" else logging.INFO

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=5)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

product_logger: logging.Logger = setup_logger('products', 'products.log')
order_logger: logging.Logger = setup_logger('orders', 'orders.log')
main_logger: logging.Logger = setup_logger('main', 'app.log')
