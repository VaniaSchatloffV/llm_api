from app.dependencies import get_settings
import logging, sys
settings = get_settings()
env = settings.environment

LOGGER = logging.getLogger(__name__)
if env == "dev":
    LOGGER.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s  [%(levelname)s]: %(message)s")
stream_handler.setFormatter(log_formatter)
LOGGER.addHandler(stream_handler)

LOGGER.info('Inicializando LOGGER')