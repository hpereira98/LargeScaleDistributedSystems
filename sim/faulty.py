from .sim import DiscreteEventSimulator

import random


class FaultySimulator(DiscreteEventSimulator):
    """ An implementation of the DiscreteEventSimulator interface.

    Arguments:
        DiscreteEventSimulator {DiscreteEventSimulator} -- Interface to implement
    """

    def __init__(self, nodes, distances, fault_chance=0, simulation_time=1000):
        """ Constructor for FaultySimulator class.

        Arguments:
            nodes {Node} -- graph nodes
            distances {array of pairs} -- distances between each node 

        Keyword Arguments:
            fault_chance {int} -- probability of losing a message in simulation (default: {0})
            simulation_time {int} -- time to run simulation in milliseconds (logical time incremented by the simulator) (default: {1000})

        Instantiated Attributes:
            nodes {Node} -- graph nodes
            current_instant -- simulator current instant tracker, based on the time of events
            distances {array of pairs} -- distances between each node 
            pending {array of events} -- contains all the events to handle (i.e. [(instant, (src, dst, data))])
            fault_chance {int} -- probability of losing a message in simulation (default: {0})
            simulation_time {int} -- time to run simulation in milliseconds (current_instant incremented by the simulator) (default: {1000})
        """

        self.nodes = nodes

        self.distances = distances

        self.current_instant = 0

        self.pending = []

        self.fault_chance = fault_chance

        self.simulation_time = simulation_time

    def start(self, initial_data, initial_node):
        """ Starts the simulation, introducing the first event in the simulation, then starts the loop.

        Arguments:
            initial_data {string} -- Content of the first event
            initial_node {string} -- Destination of the first event in the simulation

        Returns:
            [array of events] -- events that the loop generated
        """

        # starting randomizer
        random.seed()

        # creating first event [instant, (src, dst, data)]
        instant, src, dst, data = 0, None, initial_node, initial_data

        # schedule first event 
        self.pending.append((instant, (src, dst, data)))

        # run the loop
        return self.__loop__()

    def proceed(self, additional_simulation_time):
        """ Continue simulation for an additional time.

        Arguments:
            additional_simulation_time {int} -- additional time for simulation

        Returns:
            [array of events] -- events that the loop generated
        """

        self.simulation_time += additional_simulation_time

        return self.__loop__()

    def __loop__(self):
        """ Loop that delivers events to the nodes, calculates time, distances and discards events.

        Returns:
            [array of events] -- All the events that occurred in the simulation
        """

        # creating a sorted event list
        ordered_events = []

        # running loop
        while len(self.pending) > 0 and self.current_instant <= self.simulation_time:  # 1000ms maximum

            # getting the event with lowest instant
            event = min(self.pending, key=lambda e: e[0])

            # unfolding event properties
            instant, src, dst, data = event[0], event[1][0], event[1][1], event[1][2]

            # simulator time
            self.current_instant = instant

            # removing event from the queue
            self.pending.remove(event)

            # skipping event based on fault probability
            if src != dst and random.random() < self.fault_chance and src is not None:

                # print("\n[ ] {:.3f}".format(instant) + "s :: " + str(src) + " -> " + str(dst) + " :: " + str(data), end="")

                # skipping iteration
                continue

            # else:
                # print(("\n" if src is not None else "" )+ "[X] {:.3f}".format(instant) + "s :: " + str(src) + " -> " + str(dst) + " :: " + str(data), end="")

            # executing event if event is valid
            if (src, dst) in self.distances or (dst, src) in self.distances or src == dst or src is None:
                # appending event to sorted event list
                ordered_events.append(event)

                # generating new events from event
                self.__exec__(event)

        # returning sorted event list
        return ordered_events

    def __exec__(self, event):
        """ Node handles the event, and its results are translated into simulator events.

        Arguments:
            event {(instant, (src, dst, data))} -- Has information about the instant, its source, the destiny and the actual payload
        """

        # unfolding event properties
        instant, src, dst, data = event[0], event[1][0], event[1][1], event[1][2]

        # node handling event and generating new datas
        new_datas = self.nodes[dst].handle(src, data, self.current_instant)

        # update src node
        new_src = dst

        # generating events for each data
        for (new_dst, new_data, delay) in new_datas:
            # get distance to node
            distance = 0
            if (new_src, new_dst) in self.distances:
                distance = self.distances[(new_src, new_dst)]

            elif (new_dst, new_src) in self.distances:
                distance = self.distances[(new_dst, new_src)]

            # creating new event
            new_event = (instant + distance + delay, (new_src, new_dst, new_data))

            # appending event to pending
            self.pending.append(new_event)
