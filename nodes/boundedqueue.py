class BoundedQueue:

    # constructor for bounded queue
    def __init__(self, size):
        self.size = size
        self.__queue = []

    # add an element to queue and removes first if needed
    def add(self, elem):

        self.__queue.append(elem)

        if len(self.__queue) > self.size:
            self.__queue.pop(0)

    # compare a given element with the values on the queue.
    # Returns True if the element is equal to every value in the queue
    def compare(self, elem):

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
