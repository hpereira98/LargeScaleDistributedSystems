from enum import Enum


class GraphType(Enum):
    """ Different types of Graphs can be used.

    Arguments:
        Enum {Enumeration} -- type of the Graph Type
    """
    ERDOS_RENYI = 1
    BARABASI_ALBERT = 2
    WATTS_STROGATZ = 3
