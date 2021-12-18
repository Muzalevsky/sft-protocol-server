#!/usr/bin/python3 -uB

class Storage():
    def __init__(self):
        self.storage = dict()

    def add_data(self, content):
        # parse content
        return True

    def push(self, id, data):
        if id in self.storage:
            return False
        self.storage[id] = data
        return True

    def pop_by_id(self, id):
        return self.storage.pop(id)
