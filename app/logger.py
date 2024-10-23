from app.dependencies import get_settings
import logging, sys
settings = get_settings()
env = settings.environment

logging.basicConfig(
    filename="C:\\Users\\Cototo\\Desktop\\llm_api\\logging_output\\logging.log", #revisar nombre y ubicacion lol
    filemode="a",
    format="%(asctime)s  [%(levelname)s]: %(message)s"
)

LOGGER = logging.getLogger(__name__)
if env == "dev":
    LOGGER.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s  [%(levelname)s]: %(message)s")
stream_handler.setFormatter(log_formatter)
LOGGER.addHandler(stream_handler)

LOGGER.info('Inicializando LOGGER')