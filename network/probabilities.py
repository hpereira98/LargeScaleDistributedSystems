import numpy


def calculate_probability(graph, num):
    """ Calculate a list of probabilities for a graph, depending on the number of connected edges (degree).

    Arguments:
        graph {Graph} -- graph data structure
        num {int} -- number of vertices of the graph

    Returns:
        [array] -- probabilities of each node.
    """

    prob_list = []
    degrees = []

    for x in list(graph):
        degrees.append(graph.degree(x) + 1)

    s = sum(degrees)

    for x in range(num):
        prob_list.append((degrees[x] + 1) / (s + num))
    
    return prob_list


def preferential_attachment(num, probs):
    """ Make a choice given a list of probabilities

    Arguments:
        num {int} -- number of vertices of the graph
        probs {array} --  probabilities associated to each node

    Returns:
        [int] -- chosen node
    """

    if num == 0:
        return 0

    return numpy.random.choice(numpy.arange(0, num), p=probs)
