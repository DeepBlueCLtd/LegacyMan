class StatefulSuffixGenerator:
    def __init__(self):
        self.current_index = 0

    def next_value(self):
        self.current_index += 1
        return format(self.current_index, 'x')


class SequenceGenerator:
    def __init__(self):
        self.current_index = 0

    def next_value(self):
        self.current_index += 1
        return self.current_index
