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
    startPoint = 25
    path = []
    cumulate_cost = {}
    for p, c in getPath(FILE, startPoint):
        path = p
        cumulate_cost = c
    G, pos, treasure = GenMap(FILE, startPoint)
    print(path)
    print(cumulate_cost)
    drawGraph(G, pos, treasure)
    path_animation(G, pos, path, treasure, cumulate_cost)

if __name__ == "__main__":
    main()
