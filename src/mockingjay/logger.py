import logging.config
from logging import getLogger
from logging import Logger

import yaml


def get_logger(name: str) -> Logger:
    with open("src/mockingjay/logging_config.yaml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    return getLogger(name)
