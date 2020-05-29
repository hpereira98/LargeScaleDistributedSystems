from statistics import mean
import matplotlib.pyplot as plt

from benchmark.resultsproducer import produce_results
from network.graphtype import GraphType


def calculate_points(dictionary):
    """ Calculate the average of the lists of each key.

    Arguments:
        dictionary {dictionary} -- data struct that holds an array of values for each key

    Returns:
        x [array] -- array of x coordinates
        y [array] -- array of y coordinates
    """

    x = []
    y = []
    for key, value in dictionary.items():
        x.append(key)
        y.append(mean(value))

    return x, y


def draw_plot(erdos, barabasi, watts):
    fig, axs = plt.subplots(nrows=1, ncols=2, constrained_layout=False, figsize=(20, 10))
    axs[0].plot(erdos[0], erdos[1], label='Erdos-Renyi')
    axs[0].plot(barabasi[0], barabasi[1], label='Barabasi-Albert')
    axs[0].plot(watts[0], watts[1], label='Watts-Strogatz')
    axs[0].set(xlabel='Vertices', ylabel='Time (ms)', title='Time To Converge')
    axs[0].legend()

    axs[1].plot(erdos[2], erdos[3], label='Erdos-Renyi')
    axs[1].plot(barabasi[2], barabasi[3], label='Barabasi-Albert')
    axs[1].plot(watts[2], watts[3], label='Watts-Strogatz')
    axs[1].set(xlabel='Vertices', ylabel='Messages', title='Messages To Converge')
    axs[1].legend()

    plt.show()


if __name__ == '__main__':

    erdos = ([2, 4, 8, 16, 32, 64, 128], [130.0, 419.0, 769.0, 2235.0, 2201.0, 1721.0, 1440.0], [2, 4, 8, 16, 32, 64, 128], [37, 616.6, 3087.4, 18842.8, 37361.8, 62506, 108980.2])
    barabasi = ([2, 4, 8, 16, 32, 64, 128], [130.0, 418.0, 850.0, 954.0, 1352.0, 770.0, 910.0], [2, 4, 8, 16, 32, 64, 128], [37, 602.2, 3624.4, 8789.2, 25251.4, 29965, 69655])
    watts = ([2, 4, 8, 16, 32, 64, 128], [130.0, 250.0, 298.0, 361.0, 956.0, 3074.0, 5912.0], [2, 4, 8, 16, 32, 64, 128], [37, 717.4, 1703.8, 4085.2, 22603.6, 134516.8, 495046])

    draw_plot(erdos, barabasi, watts)

