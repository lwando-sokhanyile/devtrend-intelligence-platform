import logging

def setup_logging(name):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )
    return logging.getLogger(name)