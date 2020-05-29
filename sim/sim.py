class DiscreteEventSimulator:
    """
    Interface that declares abstract methods for implementations classes to implement.
    """

    # returns list of events ordered by time
    def start(self, initial_data, initial_node):
        pass

    # returns list of events ordered by time, after an additional simulation time
    def proceed(self, additional_simulation_time):
        pass
