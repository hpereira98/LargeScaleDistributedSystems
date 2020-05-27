from statistics import mean

from benchmark.resultsproducer import produce_results
from network.graphtype import GraphType


def calculate_points(dictionary):

    results = []
    for key, value in dictionary.items():
        results.append((key, mean(value)))

    return results


if __name__ == '__main__':
    __durations, __messages = produce_results(GraphType.ERDOS_RENYI, 10, 3, 5, 0, 10, 32)
    print("Erdos-Renyi:")
    print("durations:")
    print(calculate_points(__durations))
    print("messages:")
    print(calculate_points(__messages))
    __durations, __messages = produce_results(GraphType.BARABASI_ALBERT, 10, 3, 5, 0, 10, 32)
    print("Barabasi-Albert:")
    print("durations:")
    print(calculate_points(__durations))
    print("messages:")
    print(calculate_points(__messages))
