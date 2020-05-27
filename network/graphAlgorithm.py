import matplotlib.pyplot as plt
import networkx as nx
from random import randrange
from network.probabilities import calculate_probability, preferential_attachment


# create a connected component with Erdos Renyi algorithm
def erdosRenyi(num_vertices):
    graph = nx.Graph()
    for x in range(num_vertices):
        graph.add_node("(" + str(x) + ")")

    while not nx.is_connected(graph):
        i = randrange(num_vertices)
        j = randrange(num_vertices)
        if i != j:
            graph.add_edge("(" + str(i) + ")", "(" + str(j) + ")")

    return graph


# create a connected component with Barabasi Albert algorithm
def barabasiAlbert(num_vertices):
    graph = nx.Graph()
    for x in range(num_vertices):
        graph.add_node("(" + str(x) + ")")

    while not nx.is_connected(graph):
        probabilities = calculate_probability(graph, num_vertices)
        i = preferential_attachment(num_vertices, probabilities)
        j = preferential_attachment(num_vertices, probabilities)
        if i != j:
            graph.add_edge("(" + str(i) + ")", "(" + str(j) + ")")

    return graph


# create a connected component with Watts Strogatz algorithm
def wattsStrogatz(num_vertices, nearest_neighbors, rewiring_probability):

    return adapt_graph(nx.connected_watts_strogatz_graph(num_vertices, nearest_neighbors, rewiring_probability, tries=100000))


# Adapt a graph to a desired form
def adapt_graph(g):

    graph = nx.Graph()
    for node in nx.nodes(g):
        graph.add_node("(" + str(node) + ")")

    for (i, j) in nx.edges(g):
        if i != j:
            graph.add_edge("(" + str(i) + ")", "(" + str(j) + ")")

    return graph


if __name__ == "__main__":
    # G = erdosRenyi(100)
    # G = barabasiAlbert(100)
    G = wattsStrogatz(100, 10, 0.05)
    nx.draw(G, pos=nx.spring_layout(G))
    plt.show()
