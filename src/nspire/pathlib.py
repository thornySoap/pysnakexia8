"""Allow values to be stored on Nspire"""
from ti_system import recall_value, store_value


class Path:
    def __init__(self, path):
        self.path = path

    def __getattr__(self, item):
        if item == "parent":
            return self

    def __truediv__(self, other):
        self.path = other
        return self

    def resolve(self):
        return self

    def exists(self):
        try:
            recall_value(self.path)
        except TypeError:
            return False
        else:
            return True

    def touch(self):
        if not self.exists:
            self.reset()

    def reset(self):
        store_value(self.path, 0)

    def read_text(self):
        return str(recall_value(self.path))

    def write_text(self, text):
        store_value(self.path, int(text))
