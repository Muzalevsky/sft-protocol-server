#!/usr/bin/python3 -u -B
import time
import os
import logging
import subprocess

from .utils import Order_Status


class Worker():
    def __init__(self, slots_num):
        self.slots_num = slots_num
        self.slots = [0] * self.slots_num
        self.size = 0

    def fill_slot(self, element):
        # use only after "check_free_slot"
        logging.debug(f'{self.slots}')
        for i in range(self.slots_num):
            if self.slots[i] == 0:
                self.slots[i] = element
                self.size += 1
                return
        raise IndexError

    def free_slot(self, num):
        self.slots[num] = 0
        self.size -= 1

    def check_free_slot(self):
        if self.size < self.slots_num:
            return True
        return False

    def is_busy(self):
        if self.size > 0:
            return True
        return False

    def active_slots(self):
        return [ (self.slots[i], i) for i in range(self.slots_num) if self.slots[i] != 0]


class Scheduler():
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        # list of all orders
        self.orders = dict()
        # queue only with new ids
        self.queue = list()
        self.counter = 0

    def validator(self, params):
        params_list = ['lat', 'lon', 'scale', 'w', 'h', 'format']
        for par in params_list:
            if par not in params:
                self._logger.debug(f'Bad params = {params}')
                return False
        return True

    def add_order(self, params):
        self.counter += 1
        self.orders[self.counter] = [params, Order_Status.IN_QUEUE]
        self.queue.append(self.counter)
        return self.counter

    def check_order(self, id):
        # check if id exists
        if id in self.orders:
            return True
        return False

    def start_scheduler(self, pipe_conn, host, port, slots_num):
        self._logger.debug('start')
        try:
            service_path = os.environ['SFT_ROOT']
            util_path = service_path + 'sbin/worker'
            self._logger.debug(f'Worker path ={util_path}')
        except Exception as exc:
            self._logger.debug('Could not find SFT_ROOT')

        worker = Worker(slots_num)

        while True:
            # checking new data in Pipe
            if pipe_conn.poll():
                data = pipe_conn.recv()
                self._logger.debug(f'Scheduler got: {data}')

                if data[0] == 0:
                    # request for new order
                    self._logger.debug(f'Scheduler new order {data[1]}')
                    code = 0
                    protocolId = 0

                    if self.validator(data[1]):
                        protocolId = self.add_order(data[1])
                        code = 1

                    pipe_conn.send((protocolId, code))
                else:
                    # request to check order
                    self._logger.debug(f'Scheduler checking order id={data[1]}')
                    if self.check_order(data[1]):
                        self._logger.debug(f'Status: {self.orders[data[1]][1]}')
                        pipe_conn.send(self.orders[data[1]][1])
                    else:
                        self._logger.debug(f'No order in scheduler with ID {data[1]}')
                        pipe_conn.send(Order_Status.UNKNOWN)
                continue
            else:
                # print('No data for scheduler')
                pass

            # checking queue

            # if any of slots are free
            if worker.check_free_slot():
                # if current_order == False:
                if self.queue:
                    current_protocol_id = self.queue.pop(0)
                    self._logger.debug(f'Current protocol id {current_protocol_id}')
                    params = self.orders[current_protocol_id][0]
                    self._logger.debug(f'{params}')
                    child = subprocess.Popen([util_path, f'-uhttp://{host}:{port}', f'-o{current_protocol_id}',f"-x{params['lon'][0]}", f"-y{params['lat'][0]}",
                                              f"-s{params['scale'][0]}", f"-w{params['w'][0]}", f"-h{params['h'][0]}", f"-f{params['format'][0]}"])

                    worker.fill_slot((current_protocol_id, child))
                    self._logger.debug('popen')

            # if some slots are busy
            # checking if order is ready
            if worker.is_busy():
                # if child.poll() != None:
                for slot, id in worker.active_slots():
                    if slot[1].poll() is not None:
                        self._logger.debug(f'Scheduler detects process as ready, return code: {slot[1].returncode}')
                        if slot[1].returncode == 0:
                            self.orders[slot[0]][1] = Order_Status.READY
                        else:
                            self.orders[slot[0]][1] = Order_Status.ERROR
                        worker.free_slot(id)
            time.sleep(0.1)
        return 2
