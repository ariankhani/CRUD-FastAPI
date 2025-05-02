# logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file, level=None):
    # تنظیم سطح لاگ بر اساس محیط (development یا production)
    if level is None:
        level = logging.DEBUG if os.getenv("ENV") == "development" else logging.INFO

    # فرمت لاگ
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # handler برای فایل با قابلیت چرخش (rotate)
    file_handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=5)
    file_handler.setFormatter(formatter)

    # handler برای نمایش در کنسول
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ساخت logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# تعریف loggerهای مختلف
product_logger: logging.Logger = setup_logger('products', 'products.log')
order_logger: logging.Logger = setup_logger('orders', 'orders.log')
main_logger: logging.Logger = setup_logger('main', 'app.log')