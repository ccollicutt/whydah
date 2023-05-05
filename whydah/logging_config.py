import logging
import colorlog


def setup_logging():
    """
    Set up logging for the application
    """
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    color_formatter = colorlog.ColoredFormatter(f"%(log_color)s{log_format}")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    root_logger.addHandler(console_handler)
