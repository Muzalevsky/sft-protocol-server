#!/usr/bin/python3 -uB
import os


def get_log_path():
    path = os.environ['SFT_ROOT']
    path = os.path.join(path, "data", "logs", "sft-protocol-server")
    return path
