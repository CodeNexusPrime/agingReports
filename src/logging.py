import logging

logging.basicConfig(level=logging.DEBUG, filename="../log.log",filemode='w',
                    format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)