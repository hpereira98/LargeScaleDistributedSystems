import random

from .node import Node

from enum import Enum

from time import perf_counter


class HybridNode(Node):

    # - id: identification number 
    # - role: node role in the network
    # - neighbors: adjacent nodes id's
    def __init__(self, id, role, distances, initial_value, fanout):

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

        num_neighbors = len(self.neighbors)
        self.fanout = fanout if fanout <= num_neighbors else num_neighbors

        # Fault detection parameters (based on TCP)
        self.rto = {neighbor:100 for neighbor in self.neighbors} # Initial Retransmission Timeout (in miliseconds)
        self.srtt = {neighbor:-1 for neighbor in self.neighbors} # Smoothed Round-trip Time (-1 as it has no initial value)
        self.rttvar = {neighbor:-1 for neighbor in self.neighbors} # Variation in Round-trip time (-1 as it has no initial value)

        self.min_rto = 20 # Minimum Retransmission Timeout
        self.max_rto = 2000 # Maxixmum Retransmission Timeout

        # Timers to calculate RTT
        self.timers = {neighbor:-1 for neighbor in self.neighbors} # Timers for RTT

    # invoked from simulator
    def handle(self, src, data):

        # unpacking data 
        type, id, payload = data

        # handling different types of messages
        if type is MessageType.GOSSIP:

            return self.__gossip__(src, id, payload)

        elif type is MessageType.RETRANSMISSION:

            return self.__retransmission__(src, id, payload)

        elif type is MessageType.GC:

            return self.__gc__(src)

        else:

            return []

    def __send__ (self, event):

        # Adding event to the events to send to simulator
        res = [event] 

        # Creating retransmission event
        retransmission_event = (self.id, (MessageType.RETRANSMISSION, self.message_id, event), self.rto)

        # Adding retransmission event to events to return to simulator
        # res.append(retransmission_event)

        return res


    def __retransmission__ (self, id, data):

        # Destination of original message
        dst = data[0]

        # If timer was reset, then a response was received for the message
        if self.timers[dst] == -1 :
            
            return []

        # Doubling RTO
        self.rto[dst] = min (self.rto[dst] * 2, self.max_rto)

        # Re-sending message
        return self.__send__(data)

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
                self.timers[neighbor] = perf_counter() * 0.0001

                # Sending 
                res += self.__send__((neighbor, (MessageType.GOSSIP, self.message_id, (GossipType.REQUEST, self.sum, self.weight)), 0))

            fan += 1

        return res

    # send a message to one node
    def __cast__(self, dst, message_id, type):

        self.sum /= 2
        self.weight /= 2

        return self.__send__((dst, (MessageType.GOSSIP, message_id, (GossipType.RESPONSE, self.sum, self.weight)), 0))

    # checks if all neighbours have responded in this round and if such increments it
    def __increment_round__(self):

        res = []

        # multicast only when there isn't previous round and the current round isn't in the map
        # or the previous round has finished
        if self.message_id not in self.received or (len(self.received[self.message_id]) == self.fanout):

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

                # Calculating Round-trip Time with node
                rtt = perf_counter() * 0.0001 - self.timers[src]

                # Resetting timer
                self.timers[src] = -1

                # Updating RTO parameters
                if self.srtt[src] == -1 : # First RTO calculation for node

                    self.srtt[src] = rtt
                    self.rttvar[src] = rtt * 0.5
                
                else:

                    self.rttvar[src] = 0.75 * self.rttvar[src] + 0.25 * abs (self.srtt[src] - rtt)
                    self.srtt[src] = 0.875 * self.srtt[src] + 0.125 * rtt


                # Updating Retransmission Timeout
                self.rto[src] = self.srtt[src] + max( self.min_rto, 4 * self.rttvar[src] )

                # Appending src to messages received in this round
                self.received[id].append(src)

            self.sum += sum
            self.weight += weight

        return res + self.__increment_round__()



# different types of messages recognized by this type of node
class MessageType(Enum):
    GOSSIP = 1    
    RETRANSMISSION = 2



class GossipType(Enum):
    REQUEST = 1
    RESPONSE = 2


# different types of hybrid node
class HybridRole(Enum):
    PRIMARY = 1
    SECUNDARY = 2
