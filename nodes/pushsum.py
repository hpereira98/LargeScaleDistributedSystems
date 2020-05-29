import random

from .boundedqueue import BoundedQueue
from .node import Node

from enum import Enum


class PushSumNode(Node):
    """ Class that implements the behaviour of a Node

    Arguments:
        Node {Node} -- interface to implement
    """

    def __init__(self, id, distances, initial_value, fanout, nonews):
        """ Constructor for the PushSumNode

        Arguments:
            id {int} -- [description]
            distances {dictionary} -- dictionary of pairs and distances
            initial_value {int} -- value that a node holds
            fanout {int} -- fanout value that represents the number of neighbors to send a message
            nonews {int} -- number of the no news array

        Instantiated Attributes:
            id {int} -- node id
            message_id {int} -- # unique message ids
            current_instant {int} -- # instant
            sum {float} -- sum calculated value
            weight {float} -- weight calculated value
            aggregate {float} -- aggregate calculated value
            round {int} -- round info
            responded {dictionary} -- dictionary of the neighbors who have responded in each round
            requested {dictionary} -- dictionary of the neighbors who have requested each round
            neighbors {array} -- direct neighbors 
            fanout {int} -- fanout value
            rto {int} -- Initial Retransmission Timeout (in milliseconds)
            srtt {int} -- Smoothed Round-trip Time (-1 as it has no initial value)
            rttvar {int} -- Variation in Round-trip time (-1 as it has no initial value)
            min_rto {int} -- Minimum Retransmission Timeout
            max-rto {int} -- Maximum Retransmission Timeout
            timers {dictionary} -- Timers to calculate RTT
            no_news {BoundedQueue} -- Termination info
        """

        self.id = id

        self.message_id = -1

        self.current_instant = 0

        self.sum = initial_value
        self.weight = 0
        self.aggregate = self.sum

        self.round = 0

        self.responded = {}

        self.requested = {}

        self.neighbors = []
        for (src, dst) in distances.keys():
            if src == self.id:
                self.neighbors.append(dst)
            elif dst == self.id:
                self.neighbors.append(src)

        num_neighbors = len(self.neighbors)
        self.fanout = fanout if fanout <= num_neighbors else num_neighbors

        # Fault detection parameters (based on TCP)
        self.rto = {neighbor: 60 for neighbor in self.neighbors} 
        self.srtt = {neighbor: -1 for neighbor in self.neighbors}
        self.rttvar = {neighbor: -1 for neighbor in self.neighbors}
        self.min_rto = 20 
        self.max_rto = 1000 

        self.timers = {}

        self.no_news = BoundedQueue(nonews)

    def handle(self, src, data, instant):
        """ Method invoked from simulator to handle events. Handle events depending on their type.

        Arguments:
            src {string} -- origin of the event
            data {Message} -- payload of the event
            instant {int} -- time the event occurred

        Returns:
            [array] -- events produced
        """

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

        else:

            return []

    def __gossip__(self, src, id, payload):
        """ Method invoked when received a gossip message.

        Arguments:
            src {string} -- origin of the event
            id {int} -- id of the message
            payload {Message} -- Message payload

        Returns:
            [array] -- events produced
        """

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
        """ Method invoked when received a retransmission message. Retransmits an event and adjusts timeouts.

        Arguments:
            event {Event} -- event to be retransmitted

        Returns:
            [array] -- events produced
        """

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
        """ Method invoked when received an ack message. Adjust timers.

        Arguments:
            src {string} -- origin of an event
            id {int} -- id of an event

        Returns:
            [array] -- events produced
        """

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

    def __respond__(self, dst, round):
        """ Sends an aggregation pair to one specific node.

        Arguments:
            dst {string} -- destiny of the message
            round {int} -- round of that message

        Returns:
            [array] -- events produced
        """

        self.sum /= 2
        self.weight /= 2

        event = self.__identify__(
            (dst, (MessageType.GOSSIP, -1, (GossipType.RESPONSE, round, self.sum, self.weight)), 0))

        return self.__safe_send__(event)

    def __increment_round__(self):
        """ Checks if all neighbors have responded in this round and if such increments it

        Returns:
            [array] -- events produced
        """

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

    def __multi_request__(self):
        """ Multicast an aggregation pair to a fanout direct neighbors

        Returns:
            [array] -- events produced
        """

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

    def __safe_send__(self, event):
        """ Creates retransmission messages to make sure message is delivered.

        Arguments:
            event {Event} -- Event to be sent

        Returns:
            [array] -- events produced
        """

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
        """ Create an unique ID for an event.

        Returns:
            [string] -- Unique ID of a message
        """

        # Incrementing ID
        self.message_id += 1

        return "[{},{}]".format(self.id, self.message_id)

    def __identify__(self, event):
        """ Transforms event into unique event.

        Arguments:
            event {Event} -- event to be made unique.

        Returns:
            [Event] -- result event
        """

        # Unpacking event
        dst, data, delay = event
        type, id, payload = data

        # Creating unique ID for message
        id = self.__id__()

        return [dst, (type, id, payload), delay]


class MessageType(Enum):
    """ Different types of messages recognized by this type of node.

    Arguments:
        Enum {Enumeration} -- type of the class
    """
    GOSSIP = 1
    RETRANSMISSION = 2
    ACK = 3


class GossipType(Enum):
    """ Different types of Gossip Messages recognized by this type of node.

    Arguments:
        Enum {Enumeration} -- type of the Gossip Message
    """
    REQUEST = 1
    RESPONSE = 2
