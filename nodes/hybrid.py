from .node import Node

from enum import Enum

class HybridNode (Node):

    # - id: identification number 
    # - role: node role in the network
    # - neighbors: adjacent nodes id's
    def __init__ (self, id, role, neighbors):

        self.id = id
        self.role = role
        self.neighbors = neighbors


    def handle (self, src, data):
        
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


    def __gossip__ (self, src, id, payload):
        
        return [self.role, "GOSSIP", payload]

    def __ihave__ (self, src, id):  
        
        return []

    def __ack__ (self, src, id):
        
        return []

    def __ask__ (self, src, id):
        
        return []

    def __periodic__ (self, src, id):
        
        return []

    def __gc__ (self, src):
        
        return []

# different types of messages recognized by this type of node
class MessageType(Enum):
        
    GOSSIP = 1
    IHAVE = 2
    ASK = 3
    PERIODIC = 4
    GC = 5
    ACK = 6

# different types of hybrid node
class HybridRole (Enum):
        
    PRIMARY = 1
    SECUNDARY = 2
