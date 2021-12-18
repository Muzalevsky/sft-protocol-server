#!/usr/bin/python3 -uB
from enum import Enum
import os


class Order_Status(Enum):
    READY = 0
    IN_QUEUE = 1
    RENDERING = 2
    ERROR = 3
    UNKNOWN = 4


def get_log_path():
    path = os.environ['SFT_ROOT']
   
    # NOTE: will be error on Windows 
    # path += '/data/logs/sft-protocol-server/'

    path = os.path.join(path, "data", "logs", "sft-protocol-server")
    return path


from functools import wraps
from time import time

def timeit(func):
    @wraps(func)
    def wrap(*args, **kw):
        ts = time()
        result = func(*args, **kw)
        te = time()
        self._logger.debug(f"Function: {func} - done! {(te - ts):.3f}.")
        return result
    return wrap