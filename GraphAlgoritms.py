import matplotlib.pyplot as plt
import networkx as nx
from random import randrange


# create a connected component with Erdos Renyi algorithm
def erdosRenyi(num_vertices):
    graph = nx.Graph()
    for x in range(num_vertices):
        graph.add_node(x)

    while not nx.is_connected(graph):
        i = randrange(num_vertices)
        j = randrange(num_vertices)
        if i != j:
            graph.add_edge(i, j)

    return graph


if __name__ == "__main__":
    G = erdosRenyi(20)
    nx.draw(G, pos=nx.spring_layout(G))
    plt.show()
