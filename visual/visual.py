import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from MapLayout import GenMap
from getPath import getPath
from draw import drawGraph
from draw import path_animation


def main():
    FILE = "../data/big_maze_114.csv"
    path = getPath(FILE)
    G, pos, treasure = GenMap(FILE)
    drawGraph(G, pos, treasure)
    path_animation(G, pos, path, treasure)

if __name__ == "__main__":
    main()
