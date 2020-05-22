from .node import Node

from enum import Enum


class HybridNode(Node):

    # - id: identification number 
    # - role: node role in the network
    # - neighbors: adjacent nodes id's
    def __init__(self, id, role, distances, fanout, initial_value):

        self.id = id
        self.role = role

        # aggregation info
        self.sum = initial_value
        self.weight = 0
        self.aggregate = self.sum

        # round info
        self.message_id = 0
        # dictionary for received messages in some round
        self.received = {}

        # setting neighbors
        self.neighbors = []
        for (src, dst) in distances.keys():
            if src == self.id:
                self.neighbors.append(dst)
            elif dst == self.id:
                self.neighbors.append(src)

        # setting eager and lazy neighbors
        fan = 1
        self.eager = []
        self.lazy = []
        for neighbor in self.neighbors:
            if fan <= fanout:
                self.eager.append(neighbor)
            else:
                self.lazy.append(neighbor)
            fan += 1

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

        elif type is MessageType.PERIODIC:

            return self.__periodic__(src, id)

        elif type is MessageType.GC:

            return self.__gc__(src)

        else:

            return []

    # multicast pair to neighbors
    def __multicast__(self):

        res = []

        self.sum /= len(self.eager) + 1
        self.weight /= len(self.eager) + 1

        for node in self.eager:
            res.append((node, (MessageType.GOSSIP, self.message_id, (GossipType.REQUEST, self.sum, self.weight)), 0))

        for node in self.lazy:
            res.append((node, (MessageType.IHAVE, self.message_id, ""), 0))

        self.message_id += 1

        return res

    # send a message to one node
    def __cast__(self, dst, message_id):

        res = []

        self.sum /= 2
        self.weight /= 2

        res.append((dst, (MessageType.GOSSIP, message_id, (GossipType.RESPONSE, self.sum, self.weight)), 0))

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
            # print(str(self.id) + '(begin): \tsum: ' + str(round(self.sum, 5)) + ' \tweight: ' + str(round(self.weight, 5)) + ' \taggregate: ' + str(self.aggregate))

        else:
            # print(str(self.id) + '(begin): \tsum: ' + str(round(self.sum, 5)) + ' \tweight: ' + str(round(self.weight, 5)) + ' \taggregate: ' + str(self.aggregate))
            if type is GossipType.REQUEST:
                res = res + self.__cast__(src, id)
            else:
                self.received[id].append(src)

            self.sum += sum
            self.weight += weight

        # multicast only when there isn't previous round and the current round isn't in the map
        # or the previous round has finished
        if ((self.message_id - 1) not in self.received and self.message_id not in self.received) or (
                len(self.received[self.message_id - 1]) == len(self.neighbors)):
            self.received[self.message_id] = []
            res = res + self.__multicast__()

        # print('send: ' + str(res))

        self.aggregate = round(self.sum / self.weight, 3)
        # print(str(self.id) + '(end): \tsum: ' + str(round(self.sum, 5)) + ' \tweight: ' + str(round(self.weight, 5)) + ' \taggregate: ' + str(self.aggregate))

        return res

    # invoked when received a ihave message
    def __ihave__(self, src, id):

        return []

    # invoked when received an ack message
    def __ack__(self, src, id):

        return []

    # invoked when received an ask message
    def __ask__(self, src, id):

        return []

    # invoked when received a periodic message
    def __periodic__(self, src, id):

        return []

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
