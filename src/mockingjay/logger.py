import os
import logging.config
from logging import getLogger
from logging import Logger

import yaml


def get_logger(name: str) -> Logger:
    config_fpath = os.path.join(os.path.dirname(__file__), "config/logging_config.yaml")
    with open(config_fpath, "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    return getLogger(name)
