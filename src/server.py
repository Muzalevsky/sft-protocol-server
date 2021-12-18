#!/usr/bin/python3 -uB
import logging

from .net_interface import Net_Interface
from .scheduler import Scheduler
from .storage import Storage

from multiprocessing import Process, Pipe


class Server:
    def __init__(self, host: str, port: str, slots_num: int):
        self._logger = logging.getLogger(self.__class__.__name__)

        self.port = port
        self.host = host
        self.slots_num = slots_num

        self.net_interface = Net_Interface(self.host, self.port)
        self.buf_storage = Storage()
        self.scheduler = Scheduler()

    def start(self):
        # starting sheduler as a subprocess with pipe
        sched_conn, serv_conn = Pipe()
        sched = Process(target=self.scheduler.start_scheduler, args=(sched_conn, self.host, self.port, self.slots_num))
        sched.start()
        self._logger.debug("Scheduler - start!")

        # Net_Interface start with access to Buf_Storage and Scheduler
        self.net_interface.start_server(serv_conn, self.buf_storage)