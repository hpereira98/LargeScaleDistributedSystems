class Node:
    """ Interface that declares abstract methods for implementations classes to implement.
    """

    # returns e.g. [(dst0, msg0), (dst1, msg1), ...]
    def handle(self, src, data, instant):
        pass
