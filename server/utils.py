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
    try:
        path = os.environ['SFT_ROOT']
        path += '/data/logs/sft-protocol-server/'
    except:
        path = None
    return path
