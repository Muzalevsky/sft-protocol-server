#!/usr/bin/python3 -uB
from net_interface import Net_Interface
from scheduler import Scheduler
from storage import Storage
from utils import get_log_path

import argparse
import shutil
import os
import sys
import time
from multiprocessing import Process, Pipe


class Server:
    def __init__(self, host, port, slots_num):
        self.port = port
        self.host = host
        self.slots_num = slots_num

    def server_init(self, Interface_Class, Storage_Class,  Scheduler_Class):
        self.net_interface = Interface_Class(self.host, self.port)
        self.buf_storage = Storage_Class()
        self.scheduler = Scheduler_Class()

    def start(self):
        # starting sheduler as a subprocess with pipe
        sched_conn, serv_conn = Pipe()
        sched = Process(target=self.scheduler.start_scheduler, args=(sched_conn, self.host, self.port, self.slots_num))
        sched.start()

        # Net_Interface start with access to Buf_Storage and Scheduler
        self.net_interface.start_server(serv_conn, self.buf_storage)


def parse_args():
    parser = argparse.ArgumentParser(description='sft-protocol-server description:')
    parser.add_argument('address', type=str,
                help='a required string positional argument, ip-adress of server')
    parser.add_argument('port', type=int,
                help='a required integer positional argument, port of server')
    parser.add_argument('slots_num', type=int,
                help='a required integer positional argument, number of slots to render data simultaneously')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    try:
        args = parse_args()
    except Exception as exp:
        print("Arguments parsing error")
        sys.exit(1)

    # log folder (re)creating
    log_path = get_log_path()
    if log_path is None:
        print("Could not find SFT_ROOT environment variable")
        sys.exit(1)

    try:
        shutil.rmtree(log_path)
    except FileNotFoundError:
        pass
    except Exception as exc:
        print("Could not get an access to log folder", log_path, exc)
        sys.exit(1)

    try:
        os.mkdir(log_path)
    except Exception as exc:
        print("Could not create log folder", log_path, exc)
        sys.exit(1)

    try:
        new_server = Server(args.address, args.port, args.slots_num)
        new_server.server_init(Net_Interface, Storage, Scheduler)
        new_server.start()
    except KeyboardInterrupt:
        print('Server is closed')
        sys.exit(0)
