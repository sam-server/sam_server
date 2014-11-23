
class ParseError(Exception):
    def __init__(self, position, reason):
        self.position = int(position)
        self.reason = reason

    def __str__(self):
        return 'Error parsing input at {0.position}: {0.reason}'.format(self)


class StateError(Exception):
    pass

