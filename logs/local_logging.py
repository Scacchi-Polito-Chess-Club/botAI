import logging
import sys
from datetime import datetime as time


def make_logger(log):
    logger = None
    if log is not None:
        logger = logging.getLogger("botAI")
        if type(log) is str:
            if log == "stdout":
                handler = logging.StreamHandler(stream=sys.stdout)
                handler.setLevel(logging.INFO)

            elif log == "logfile":
                handler = logging.FileHandler(time.now().strftime("%Y:%m:%d-%H:%M:%S.log"))
                handler.setLevel(logging.INFO)
                formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
            else:
                raise ValueError(f"{log} is not a valid logger.")
            logger.addHandler(handler)

        elif type(log) is list or type(log) is tuple:
            for l in log:
                if l == "stdout":
                    handler = logging.StreamHandler(stream=sys.stdout)
                    handler.setLevel(logging.INFO)

                elif l == "logfile":
                    handler = logging.FileHandler(time.now().strftime("%Y:%m:%d-%H:%M:%S.log"))
                    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                    handler.setFormatter(formatter)
                    handler.setLevel(logging.INFO)
                else:
                    raise ValueError(f"{l} is not a valid logger.")
                logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
