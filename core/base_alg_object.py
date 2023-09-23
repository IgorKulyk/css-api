import os
import sys
from pathlib import Path
import toml
import logging
from logging.handlers import RotatingFileHandler


def configure_log(name, folder, logger_name=None, level=logging.DEBUG):
    use_console = True
    date_format = "%y-%m-%d %H:%M:%S"
    # date_format = "%H:%M:%S"
    message_format = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
    formatter = logging.Formatter(fmt=message_format, datefmt=date_format)
    os.makedirs(folder, exist_ok=True)
    log_file = os.path.join(folder, f'{name}.log')
    file_handler = RotatingFileHandler(log_file, mode='w', encoding='utf8', maxBytes=1000000, backupCount=3)
    # file_handler = logging.FileHandler(log_file, mode='w', encoding='utf8')
    handlers = []
    handlers.append(file_handler)
    if use_console:
        console_handler = logging.StreamHandler()
        handlers.append(console_handler)
    logger = logging.getLogger() if logger_name is None else logging.getLogger(logger_name)
    logger.setLevel(level)  # TODO from config
    for h in handlers:
        h.setLevel(level)
        h.setFormatter(formatter)
    logger.handlers = handlers
    # logger.addHandler(h)
    return logger


def get_config():
    config = None
    try:
        base_path = Path(__file__).parent.parent
        config_file_name = os.path.join(base_path, 'sys_config.toml')
        config_file_name = os.path.abspath(config_file_name)
        config = toml.load(config_file_name)
    except FileNotFoundError as e:
        print(f"@@@ Missing system configuration file 'sys_config.toml'. Copy to local file from sys_config.toml")
        config = None
    return config


class BaseAlgObject:
    config = get_config()
    root_module = sys.modules['__main__']
    try:
        file_name = root_module.__getattribute__('__file__')
        app_name = os.path.basename(root_module.__file__).split('.')[0]
    except AttributeError as ex:
        app_name = root_module.sys.argv[0].split('.')[0]

    # logger = logging.getLogger()
    logger = configure_log(name=app_name, folder='log', logger_name=app_name)