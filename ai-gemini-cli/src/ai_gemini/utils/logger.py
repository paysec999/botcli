import logging

def setup_logger():
    # Configure the logger
    logger = logging.getLogger("ai_gemini")
    logger.setLevel(logging.DEBUG)

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)
    return logger

def log_info(message):
    logger = setup_logger()
    logger.info(message)

def log_warning(message):
    logger = setup_logger()
    logger.warning(message)

def log_error(message):
    logger = setup_logger()
    logger.error(message)

def log_debug(message):
    logger = setup_logger()
    logger.debug(message)
