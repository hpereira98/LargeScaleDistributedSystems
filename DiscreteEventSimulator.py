class Simulator:
    def __init__(self, nodes, distances):
        self.nodes = nodes
        self.distances = distances
        self.current_time = 0
        self.pending = []  # [(instant, (src, dst, MessageType, args))]

    def start(self, initial_msg):
        pass

    def loop(self):
        pass
