import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger():
    logger = logging.getLogger("RequestLogger")
    logger.setLevel(logging.INFO)

    # Log faylini har bir kunda tozalash
    handler = TimedRotatingFileHandler(
        "request_logs.log", when="midnight", interval=1, backupCount=5
    )

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


if __name__ == "__main__":
    logger = setup_logger()
    logger.info("Test log!")
