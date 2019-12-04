import logging
from config import LOGFILE_PATH

def get_logger() -> logging.Logger:
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
            handlers=[logging.StreamHandler(),
                      logging.FileHandler(LOGFILE_PATH, mode='a')
                      ],
    )
    return logging.getLogger()

