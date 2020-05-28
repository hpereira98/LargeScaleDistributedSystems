import numpy


# calculate a list of probabilities for a graph
# depending on the number of connected edges (degree)
def calculate_probability(graph, num):
    prob_list = []
    degrees = []

    for x in list(graph):
        degrees.append(graph.degree(x) + 1)

    s = sum(degrees)

    for x in range(num):
        prob_list.append((degrees[x] + 1) / (s + num))
    return prob_list


# make a choice given a list of probabilities
def preferential_attachment(num, probs):
    if num == 0:
        return 0
    return numpy.random.choice(numpy.arange(0, num), p=probs)
