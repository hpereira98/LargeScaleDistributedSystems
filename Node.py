from enum import Enum


class Node:
    # all return e.g. [(dst0, msg0), (dst1, msg1), ...]
    def handle_gossip(self, src, identifier, payload):
        pass

    def handle_ihave(self, src, identifier):
        pass

    def handle_ack(self, src, identifier):
        pass

    def handle_ask(self, src, identifier):
        pass

    def handle_periodic(self, src, identifier):
        pass

    def handle_gc(self, src):
        pass


class MessageType(Enum):
    GOSSIP = 1
    IHAVE = 2
    ASK = 3
    PERIODIC = 4
    GC = 5
    ACK = 6
