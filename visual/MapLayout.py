import pandas as pd
import networkx as nx
import numpy as np
import collections

FILE = "../maze.csv"
SPACE = 3
def GenMap(file) :
    df = pd.read_csv(file, index_col='index')
    G = nx.DiGraph()
    TreasureIdx = []
    treasure = []
    dir_map = {'North': np.array([0, 1]), 'East': np.array([1, 0]), 'South': np.array([0, -1]), 'West': np.array([-1, 0])}
    center_x_y = [np.array([0, 0]) for _ in range(len(df))]
    for index, row in df.iterrows():
        G.add_node(index)
        near = 0
        for col_name in df.columns[0:4]:
            if pd.notna(row[col_name]):
                G.add_edge(index, int(row[col_name]), direction=col_name)                 
                near += 1
        if near <= 1 and index != 1:
            TreasureIdx.append(index)
    queue = collections.deque([1])
    visited = {1}
    while queue:
        u = queue.popleft()
        for v in G.neighbors(u):
            if v not in visited:
                direction = G[u][v]['direction']
                center_x_y[v-1] = center_x_y[u-1] + dir_map[direction]
                if v in TreasureIdx:
                    treasure.append((v, int(abs(center_x_y[v-1][0])+abs(center_x_y[v-1][1]))))
                #print(f"{v}: {center_x_y[v-1]} by {u}")
                visited.add(v)
                queue.append(v) 
    #print(center_x_y)
    pos = {i + 1: (p[0] * SPACE, p[1] * SPACE) for i, p in enumerate(center_x_y)}
    #print(pos)
    #print(treasure)
    return G, pos, treasure

if  __name__ == "__main__":
    GenMap(FILE)