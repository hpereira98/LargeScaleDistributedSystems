import concurrent.futures

from network.graphtype import GraphType
from nodes.pushsum import PushSumNode, MessageType, GossipType
from network.graphAlgorithm import erdosRenyi, barabasiAlbert
from sim.faulty import FaultySimulator


def create_topology(graph_type, vertices, initial_value, fanout, no_news):

    graph = None

    if graph_type is GraphType.ERDOS_RENYI:

        graph = erdosRenyi(vertices)

    elif graph_type is GraphType.BARABASI_ALBERT:

        graph = barabasiAlbert(vertices)

    nodes = {}
    distances = {}
    for (src, dst) in graph.edges:
        distances[(src, dst)] = 10

    for i in graph.nodes:
        nodes[i] = (PushSumNode(i, distances, initial_value, fanout, no_news))

    return nodes, distances


def run(graph_type, vertices, initial_value, fanout, no_news, error_percentage):

    nodes, distances = create_topology(graph_type, vertices, initial_value, fanout, no_news)

    faulty_sim = FaultySimulator(nodes, distances, error_percentage, 1000000)

    msg = (MessageType.GOSSIP, -1, (GossipType.REQUEST, 0, 0, 0))

    events = faulty_sim.start(msg, "(0)")

    message_count = 0
    for event in events:
        if event[1][2][0] is MessageType.GOSSIP or event[1][2][0] is MessageType.RETRANSMISSION or event[1][2][0] is MessageType.ACK:
            message_count += 1

    return vertices, faulty_sim.current_instant, message_count


def produce_results(graph_type, initial_value, fanout, no_news, error_percentage, times=10, max_bound=252):

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:

        workers = []
        i = 2
        while i <= max_bound:
            for _ in range(times):
                workers.append(executor.submit(run, graph_type, i, initial_value, fanout, no_news, error_percentage))
            i *= 2

        # append all the execution results to a list
        results = []
        for worker in concurrent.futures.as_completed(workers):
            results.append(worker.result())
            print(worker.result())

        return results


if __name__ == '__main__':
    produce_results(GraphType.BARABASI_ALBERT, 10, 3, 5, 0.1, 10, 32)
