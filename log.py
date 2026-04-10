import logging

class fmt_handler(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.detail_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.simple_fmt = logging.Formatter("%(name)s - %(message)s")

    def format(self, record):
        if record.name == "__main__" or record.name == "scoreboard":
            return self.detail_fmt.format(record)
        else:
            return self.simple_fmt.format(record)

def setup_logging():
    root_logger = logging.getLogger()
    #main level
    root_logger.setLevel(logging.INFO)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    handler = logging.FileHandler('system.log', mode='w', encoding='utf-8')
    
    handler.setFormatter(fmt_handler())
    
    root_logger.addHandler(handler)

    logging.getLogger("stdoutParser").setLevel(logging.DEBUG)
    logging.getLogger("scoreboard").setLevel(logging.DEBUG)
    
    logging.getLogger("stdoutParser").propagate = True
    logging.getLogger("scoreboard").propagate = True