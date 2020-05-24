import random

from .node import Node

from enum import Enum

from time import perf_counter


class HybridNode(Node):

    # - id: identification number 
    # - role: node role in the network
    # - neighbors: adjacent nodes id's
    def __init__(self, id, role, distances, initial_value, fanout, ihave_timeout):

        self.id = id
        self.role = role
        self.ihave_timeout = ihave_timeout
        
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

        # Fault detection timeouts (based on TCP)
        self.rto = {neighbor:1000 for neighbor in self.neighbors} # Initial Retransmission Timeout (in miliseconds)
        self.srtt = {neighbor:-1 for neighbor in self.neighbors} # Smoothed Round-trip Time (-1 as it has no initial value)
        self.rttvar = {neighbor:-1 for neighbor in self.neighbors} # Variation in Round-trip time (-1 as it has no initial value)

        self.min_rto = 20 # Minimum Retransmission Timeout

        # Timers to calculate RTT
        self.timers = dict()

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
                # Starting timer when sending a GOSSIP_REQUEST
                self.timers[neighbor] = perf_counter()
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

        # Starting timer when sending a GOSSIP_REQUEST
        if type is GossipType.REQUEST:
            self.timers[dst] = perf_counter()

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
            #self.timers = dict()
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

                # Calculating Round-trip Time with node
                rtt = perf_counter() - self.timers[src]

                # Updating RTO parameters
                if self.srtt[src] == -1 : # First RTO calculation for node

                    self.srtt[src] = rtt
                    self.rttvar[src] = rtt * 0.5
                
                else:

                    self.rttvar[src] = 0.75 * self.rttvar[src] + 0.25 * abs (self.srtt[src] - rtt)
                    self.srtt[src] = 0.875 * self.srtt[src] + 0.125 * rtt


                # Updating Retransmission Timeout
                self.rto[src] = self.srtt[src] + max( self.min_rto, 4 * self.rttvar[src] )

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

            res.append((self.id, (MessageType.PERIODIC, id, src), self.ihave_timeout))

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
