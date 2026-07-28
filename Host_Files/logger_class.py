import os
import logging
from datetime import datetime

class APILogger:
    def __init__(self, log_dir="logs"):
        """
        Initialise a logger that creates daily log files: ollama_api_log_yyyymmdd.log
        """
        # Create log directory if it doesn't exist
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up logger
        self.logger = logging.getLogger("APILogger")
        self.logger.setLevel(logging.DEBUG)
        
        # Only add handler if none exist
        if not self.logger.handlers:
            # Daily log file with today's date
            today = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(log_dir, f"ollama_api_log_{today}.log")
            
            handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _format_message(self, message: str) -> str:
        """Replace newlines with spaces to keep log lines compact."""
        return message.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    
    def _check_and_rotate(self):
        """Check if we need to rotate to a new daily log file."""
        today = datetime.now().strftime("%Y%m%d")
        expected_log = os.path.join(self.log_dir, f"ollama_api_log_{today}.log")
        current_log = self.logger.handlers[0].baseFilename if self.logger.handlers else None
        
        if not current_log or current_log != expected_log:
            # Remove old handler
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)
            
            # Create new handler for today
            new_handler = logging.FileHandler(expected_log, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            new_handler.setFormatter(formatter)
            self.logger.addHandler(new_handler)
    
    def log_info(self, message: str) -> None:
        self._check_and_rotate()
        self.logger.info(self._format_message(message))
    
    def log_warning(self, message: str) -> None:
        self._check_and_rotate()
        self.logger.warning(self._format_message(message))
    
    def log_error(self, message: str) -> None:
        self._check_and_rotate()
        self.logger.error(self._format_message(message))
    
    def log_critical(self, message: str) -> None:
        self._check_and_rotate()
        self.logger.critical(self._format_message(message))
    
    def log_fatal(self, message: str) -> None:
        self._check_and_rotate()
        self.logger.fatal(self._format_message(message))
    
    def __str__(self):
        return f"API Logger with logging directory {self.log_dir}"
    
    def __repr__(self):
        return f"APILogger(log_dir={self.log_dir})"

    def __hash__(self):
        return hash((self.logger,self.log_dir))

    def __eq__(self, other):
        if not(isinstance(other,APILogger)):
            return False
        return self.__hash__() == other.__hash__()