import random

from .boundedqueue import BoundedQueue
from .node import Node

from enum import Enum


class PushSumNode(Node):

    # - id: identification number 
    # - role: node role in the network
    # - neighbors: adjacent nodes id's
    def __init__(self, id, distances, initial_value, fanout, nonews):

        # node id
        self.id = id

        # unique message ids
        self.message_id = -1

        # instant
        self.current_instant = 0

        # aggregation info
        self.sum = initial_value
        self.weight = 0
        self.aggregate = self.sum

        # round info
        self.round = 0

        # dictionary of the neighbors who have responded in each round
        self.responded = {}

        # dictionary of the neighbors who have requested each round
        self.requested = {}

        # setting neighbors
        self.neighbors = []
        for (src, dst) in distances.keys():
            if src == self.id:
                self.neighbors.append(dst)
            elif dst == self.id:
                self.neighbors.append(src)

        num_neighbors = len(self.neighbors)
        self.fanout = fanout if fanout <= num_neighbors else num_neighbors

        # Fault detection parameters (based on TCP)
        self.rto = {neighbor: 60 for neighbor in self.neighbors}  # Initial Retransmission Timeout (in miliseconds)
        self.srtt = {neighbor: -1 for neighbor in
                     self.neighbors}  # Smoothed Round-trip Time (-1 as it has no initial value)
        self.rttvar = {neighbor: -1 for neighbor in
                       self.neighbors}  # Variation in Round-trip time (-1 as it has no initial value)

        self.min_rto = 20  # Minimum Retransmission Timeout
        self.max_rto = 1000  # Maximum Retransmission Timeout

        # Timers to calculate RTT
        self.timers = {}  # Timers for RTT

        # Termination info
        self.no_news = BoundedQueue(nonews)

    # invoked from simulator
    def handle(self, src, data, instant):

        # saving simulator instant
        self.current_instant = instant

        # unpacking data 
        type, id, payload = data

        # handling different types of messages
        if type is MessageType.GOSSIP:

            return self.__gossip__(src, id, payload)

        elif type is MessageType.RETRANSMISSION:

            return self.__retransmission__(payload)

        elif type is MessageType.ACK:

            return self.__ack__(src, id)

        elif type is MessageType.GC:

            return self.__gc__(src)

        else:

            return []

    # invoked when received a gossip message
    def __gossip__(self, src, id, payload):

        # triplet received
        type, round, sum, weight = payload

        # for returning
        res = []

        # case i'm the initial node
        if src is None:

            self.weight = 1

        else:

            if type is GossipType.REQUEST and (round not in self.requested or src not in self.requested[round]):

                # If its a round I haven't been tracking yet
                if round not in self.requested:
                    self.requested[round] = []

                # Adding request to received messages                
                self.requested[round].append(src)

                # Responding to src
                res += self.__respond__(src, round)

                # Changing my values
                self.sum += sum
                self.weight += weight

                # Appending ACK
                res.append((src, (MessageType.ACK, id, []), 0))

            elif type is GossipType.REQUEST:

                # Appending ACK
                res.append((src, (MessageType.ACK, id, []), 0))

                return res

            elif type is GossipType.RESPONSE and src not in self.responded[round]:

                # Adding request to received messages
                self.responded[round].append(src)

                # Changing my values
                self.sum += sum
                self.weight += weight

                # Appending ACK 
                res.append((src, (MessageType.ACK, id, []), 0))

            elif type is GossipType.RESPONSE:

                # Appending ACK
                res.append((src, (MessageType.ACK, id, []), 0))

                return res

        return res + self.__increment_round__()

    def __retransmission__(self, event):

        # Unpacking event
        dst, data, delay = event
        type, id, payload = data

        # If timer was reset, then a response was received for the message
        if id not in self.timers:
            # print(" :: Not resending!", end="")
            return []

        # print(" :: Resending!", end="")

        # Doubling RTO
        self.rto[dst] = min(self.rto[dst] * 2, self.max_rto)

        # Re-sending message
        return self.__safe_send__(event)

    def __ack__(self, src, id):

        # Calculating Round-trip Time with node
        rtt = self.current_instant - self.timers[id]

        # Resetting timer
        del self.timers[id]

        # Updating RTO parameters
        if self.srtt[src] == -1:  # First RTO calculation for node

            self.srtt[src] = rtt
            self.rttvar[src] = rtt * 0.5

        else:

            self.rttvar[src] = 0.75 * self.rttvar[src] + 0.25 * abs(self.srtt[src] - rtt)
            self.srtt[src] = 0.875 * self.srtt[src] + 0.125 * rtt

        # Updating Retransmission Timeout
        self.rto[src] = self.srtt[src] + max(self.min_rto, 4 * self.rttvar[src])

        # print(" :: New RTO with {}: {}".format(src, self.rto[src]), end="")

        return []

    # send a message to one node
    def __respond__(self, dst, round):

        self.sum /= 2
        self.weight /= 2

        event = self.__identify__(
            (dst, (MessageType.GOSSIP, -1, (GossipType.RESPONSE, round, self.sum, self.weight)), 0))

        return self.__safe_send__(event)

    # checks if all neighbours have responded in this round and if such increments it
    def __increment_round__(self):

        res = []

        self.aggregate = round(self.sum / self.weight, 3)

        # multicast only when there isn't previous round and the current round isn't in the map
        # or the previous round has finished
        if (self.round not in self.responded or (len(self.responded[self.round]) == self.fanout)) and not self.no_news.compare(self.aggregate):

            # increment current round
            self.round += 1
            self.responded[self.round] = []

            res += self.__multi_request__()

        self.no_news.add(self.aggregate)

        return res

    # multicast pair to neighbors
    def __multi_request__(self):

        res = []

        self.sum /= self.fanout + 1
        self.weight /= self.fanout + 1

        random.shuffle(self.neighbors)

        fan = 1
        for neighbor in self.neighbors:

            if fan <= self.fanout:
                # Gossip Request event
                event = self.__identify__(
                    (neighbor, (MessageType.GOSSIP, -1, (GossipType.REQUEST, self.round, self.sum, self.weight)), 0))

                # Sending 
                res += self.__safe_send__(event)

            fan += 1

        return res

    # Creates retransmission messages to make sure message is delivered
    def __safe_send__(self, event):

        # Adding event with unique subround number
        res = [event]

        # Waiting for aknowledgment of message
        self.timers[event[1][1]] = self.current_instant

        # Creating retransmission event
        retransmission_event = self.__identify__((self.id, (MessageType.RETRANSMISSION, -1, event), self.rto[event[0]]))

        # Adding retransmission event to events to return to simulator
        res += [retransmission_event]

        return res

    def __id__(self):

        # Incrementing ID
        self.message_id += 1

        return "[{},{}]".format(self.id, self.message_id)

    # Transforms event into unique event
    def __identify__(self, event):

        # Unpacking event
        dst, data, delay = event
        type, id, payload = data

        # Creating unique ID for message
        id = self.__id__()

        return [dst, (type, id, payload), delay]


# different types of messages recognized by this type of node
class MessageType(Enum):
    GOSSIP = 1
    RETRANSMISSION = 2
    ACK = 3
    GC = 4


class GossipType(Enum):
    REQUEST = 1
    RESPONSE = 2
