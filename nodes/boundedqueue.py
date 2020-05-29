class BoundedQueue:
    """ 
    Implementation of a bounded queue with 2 methods.
    """

    def __init__(self, size):
        """ Constructor for a Bounded Queue.

        Arguments:
            size {int} -- size of the queue

        Instantiated Attributes:
            size {int} -- maximum size of the queue
            __queue {array} -- array containing the elements of the queue
        """
        self.size = size
        self.__queue = []

    def add(self, elem):
        """ Add an element to the queue and removes the first if needed to maintain the maximum size of the queue

        Arguments:
            elem {any} -- element to add to the queue
        """

        self.__queue.append(elem)

        if len(self.__queue) > self.size:
            self.__queue.pop(0)

    def compare(self, elem):
        """ Compare a given element with the values in the queue.

        Arguments:
            elem {any} -- element to compare with thw values in the queue

        Returns:
            Boolean -- True if the element is equal to every value in the queue, False otherwise
        """

        if len(self.__queue) == 0:
            return False

        for value in self.__queue:
            if value != elem:
                return False

        return True


if __name__ == "__main__":
    queue = BoundedQueue(3)
    print(queue.compare(1))
    queue.add(2)
    queue.add(1)
    queue.add(1)
    print(queue.compare(1))
    queue.add(1)
    print(queue.compare(1))
