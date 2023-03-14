import os
from loguru import logger

logs_dir = os.path.abspath(os.path.dirname(__file__))

log_dir_name = 'logs_files'
log_file_name = 'logs.log'

log_file_path = os.path.join(logs_dir, log_dir_name, log_file_name)

logger.add(log_file_path,
           format='{time:YYYY-DD-MM|HH:mm:ss}|{level}|{message}',
           level='DEBUG',
           rotation="1 MB",
           compression="zip",
           )
