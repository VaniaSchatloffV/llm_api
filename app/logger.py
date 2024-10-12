import logging, sys

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s  [%(levelname)s]: %(message)s")
stream_handler.setFormatter(log_formatter)
LOGGER.addHandler(stream_handler)

LOGGER.info('Inicializando LOGGER')