#!/usr/bin/python3 -uB

class Storage():
    def __init__(self):
        self.storage = dict()

    def add_data(self, content):
        # parse content
        return True

    def push(self, id, data, img_format):
        if id in self.storage:
            return False
        self.storage[id] = (data, img_format)
        return True

    def pop_by_id(self, id):
        # if id in self.storage:
        #     return False
        return self.storage.pop(id)
