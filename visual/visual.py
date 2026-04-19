import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from stdoutParser import Execute_and_Parse
from layout import Layout
from animation import drawGraph
from animation import aniAlgo
from geometry import get_arc_midpoint


# f = open('filemap.txt', 'r')
# numberOfVertex, numberOfEdges = map(int, f.readline().split())
# print(numberOfVertex, numberOfEdges, sep = ", ")
# for line in f.readlines():
#     print(line, end = '')
# f.close()

dir_map = {'north': 0, 'east': 1, 'south': 2, 'west': 3}

Vertexs, Paths = Execute_and_Parse(dir_map)
print(Paths)
G, pos = Layout(Vertexs)
drawGraph(G, pos)
#aniAlgo(G, pos, Paths)

