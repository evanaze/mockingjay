import os
import logging

from mockingjay.cli import cli


# Initialize the root logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=os.getenv("LOGLEVEL", "INFO"),
)
logger = logging.getLogger(__name__)
logger.info("Starting program.")

cli()
