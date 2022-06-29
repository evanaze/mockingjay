from logging import getLogger

from mockingjay.cli import cli


# Initialize the root logger
LOGGER = getLogger(__name__)
LOGGER.info("Starting program.")

cli()
