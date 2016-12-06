from collections import namedtuple

class Route(namedtuple('Flight', ['from_code', 'to_code', 'mode'])):

    def key(self):
        return self[:2]

    def reversed_key(self):
        return self[:2][::-1]

    def __reversed__(self):
        return self.__class__(self.to_code, self.from_code, *self[2:])







