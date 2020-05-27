from enum import Enum


class GraphType(Enum):
    ERDOS_RENYI = 1
    BARABASI_ALBERT = 2
    RANDOM_GEOMETRIC = 3
    WATTS_STROGATZ = 4
