import random

class DiscreteEventSimulator:
    
    def __init__(self, nodes, distances, fault_chance = 0):
        
        # nodes
        self.nodes = nodes

        # distances between nodes
        self.distances = distances

        # simulator current instant tracker
        self.current_instant = 0

        # events pending execution [(instant, (src, dst, data))]
        self.pending = []  

        # probability of losing an event
        self.fault_chance = fault_chance

    def start(self, initial_data, initial_node):
        
        pass

    def loop(self):
        
        pass

class SimulatorImplementation (Simulator):

    def start(self, initial_data, initial_node):
        
        # starting randomizer
        random.seed()
        
        # creating first event [instant, (src, dst, data)]
        instant, src, dst, data = 0, None, initial_node, initial_data
        
        # schedule first event 
        self.pending.append( (instant, (src, dst, data )) )
        
        # run the loop
        return self.loop()

    def loop(self):
        
        # creating a sorted event list
        ordered_events = []

        # running loop
        while len(self.pending) > 0:

            # getting the event with lowest instant
            event = min (self.pending, key = lambda e:e[0])

            # unfolding event properties
            instant, src, dst, data = event[0], event[1][0], event[1][1], event[1][2]

            # printing event
            # print(str(instant) + "s :: " + str(src) + " -> " + str(dst) + " :: " + str(data))

            # removing event from the queue
            self.pending.remove(event)
        
            # skipping event based on fault probability
            if random.random() < self.fault_chance:

                # skipping iteration
                continue

            # executing event if event is valid
            if (src, dst) in self.distances or src is None:

                # appending event to sorted event list
                ordered_events.append(event)

                # generating new events from event
                self.__exec__(event)

        # returning sorted event list
        return ordered_events

    def __exec__ (self, event):

        # unfolding event properties
        instant, src, dst, data = event[0], event[1][0], event[1][1], event[1][2]

        # node handling event and generating new datas
        new_datas = self.nodes[dst].handle(src, data)

        # update src node
        new_src = dst

        # generating events for each data
        for (new_dst, new_data, delay) in new_datas:

            # get distance to node
            distance = self.distances[(new_src, new_dst)]

            # creating new event
            new_event = (instant + distance + delay, (new_src, new_dst, new_data))

            # appending event to pending
            self.pending.append(new_event)