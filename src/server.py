#!/usr/bin/python3 -uB
import logging

from .net_interface import Net_Interface
from .storage import Storage


class Server:
    def __init__(self, host: str, port: str):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.port = port
        self.host = host
        self.net_interface = Net_Interface(self.host, self.port)
        self.buf_storage = Storage()

    def start(self):
        # Net_Interface start with access to Buf_Storage and Scheduler
        self.net_interface.start_server(self.buf_storage)
