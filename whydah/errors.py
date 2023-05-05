import logging

class AppError(Exception):
    def __init__(self, message, status_code=400, error=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        if error:
            logging.error(f"AppError: {message}. Full error: {error}")
        else:
            logging.error(f"AppError: {message}")
