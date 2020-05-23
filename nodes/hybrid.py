import random

from .node import Node

from enum import Enum


class HybridNode(Node):

    # - id: identification number 
    # - role: node role in the network
    # - neighbors: adjacent nodes id's
    def __init__(self, id, role, distances, initial_value, fanout, timeout):

        self.id = id
        self.role = role
        self.timeout = timeout

        # aggregation info
        self.sum = initial_value
        self.weight = 0
        self.aggregate = self.sum

        # round info
        self.message_id = 0
        # dictionary for received messages in some round
        self.received = {}
        # dictionary for ihave messages
        self.identifiers = {}

        # setting neighbors
        self.neighbors = []
        for (src, dst) in distances.keys():
            if src == self.id:
                self.neighbors.append(dst)
            elif dst == self.id:
                self.neighbors.append(src)

        num_neighbors = len(self.neighbors)
        self.fanout = fanout if fanout <= num_neighbors else num_neighbors

    # invoked from simulator
    def handle(self, src, data):

        # unpacking data 
        type, id, payload = data

        # handling different types of messages
        if type is MessageType.GOSSIP:

            return self.__gossip__(src, id, payload)

        elif type is MessageType.IHAVE:

            return self.__ihave__(src, id)

        elif type is MessageType.ASK:

            return self.__ask__(src, id)

        elif type is MessageType.ACK:

            return self.__ack__(src, id)

        elif type is MessageType.PERIODIC:

            return self.__periodic__(src, id, payload)

        elif type is MessageType.GC:

            return self.__gc__(src)

        else:

            return []

    # multicast pair to neighbors
    def __multicast__(self):

        res = []

        self.sum /= self.fanout + 1
        self.weight /= self.fanout + 1

        random.shuffle(self.neighbors)

        fan = 1
        for neighbor in self.neighbors:
            if fan <= self.fanout:
                res.append((neighbor, (MessageType.GOSSIP, self.message_id, (GossipType.REQUEST, self.sum, self.weight)), 0))
            else:
                res.append((neighbor, (MessageType.IHAVE, self.message_id, ""), 0))

            fan += 1

        return res

    # send a message to one node
    def __cast__(self, dst, message_id, type):

        res = []

        self.sum /= 2
        self.weight /= 2

        res.append((dst, (MessageType.GOSSIP, message_id, (type, self.sum, self.weight)), 0))

        return res

    def __increment_round__(self):

        res = []

        # multicast only when there isn't previous round and the current round isn't in the map
        # or the previous round has finished
        if self.message_id not in self.received or (len(self.received[self.message_id]) == len(self.neighbors)):

            # send an ack to every node that sent me an ihave with an id == self.message_id
            if self.message_id in self.identifiers:
                for node in self.identifiers[self.message_id]:
                    res.append((node, (MessageType.ACK, self.message_id, ''), 0))

            # increment current round
            self.message_id += 1
            self.received[self.message_id] = []
            res = res + self.__multicast__()

        self.aggregate = round(self.sum / self.weight, 3)

        return res

    # invoked when received a gossip message
    def __gossip__(self, src, id, payload):

        # triplet received
        type, sum, weight = payload

        # for returning
        res = []

        # case i'm the initial node
        if src is None:
            self.weight = 1

        else:
            if type is GossipType.REQUEST:
                res = res + self.__cast__(src, id, GossipType.RESPONSE)

            else:
                self.received[id].append(src)

            self.sum += sum
            self.weight += weight

        return res + self.__increment_round__()

    # invoked when received a ihave message
    def __ihave__(self, src, id):

        res = []

        # if the received round is greater than mine
        if id > self.message_id:
            if id not in self.identifiers:
                self.identifiers[id] = []

            self.identifiers[id].append(src)

            res.append((self.id, (MessageType.PERIODIC, id, src), self.timeout))

        else:
            res.append((src, (MessageType.ACK, id, ''), 0))

        return res

    # invoked when received an ack message
    def __ack__(self, src, id):

        self.received[id].append(src)

        return self.__increment_round__()

    # invoked when received an ask message
    def __ask__(self, src, id):

        return self.__cast__(src, id, GossipType.REQUEST)

    # invoked when received a periodic message
    def __periodic__(self, src, id, dst):

        res = []

        # if the received round is still greater than mine
        if id > self.message_id and id in self.identifiers:
            self.identifiers[id].remove(dst)
            res.append((dst, (MessageType.ASK, id, ''), 0))

        else:
            res.append((dst, (MessageType.ACK, id, ''), 0))

        return res

    # invoked when received a garbageCollection message
    def __gc__(self, src):

        return []


# different types of messages recognized by this type of node
class MessageType(Enum):
    GOSSIP = 1
    IHAVE = 2
    ASK = 3
    PERIODIC = 4
    GC = 5
    ACK = 6


class GossipType(Enum):
    REQUEST = 1
    RESPONSE = 2


# different types of hybrid node
class HybridRole(Enum):
    PRIMARY = 1
    SECUNDARY = 2
