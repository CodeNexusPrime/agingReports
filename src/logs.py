import logging

# logging.basicConfig(level=logging.DEBUG, filename="log.log",filemode='w',
#                     format="%(asctime)s - %(levelname)s - %(message)s")

class Logger:
    def __init__(self, log_file="app.log", log_level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        #Prevent duplicate handlers
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def get_logger(self):
        return self.logger