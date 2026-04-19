import pandas as pd
import networkx as nx
import numpy as np
import collections

FILE = "../data/medium_maze.csv"
SPACE = 3
def GenMap() :
    df = pd.read_csv(FILE, index_col='index')
    G = nx.DiGraph()
    dir_map = {'North': np.array([0, 1]), 'East': np.array([1, 0]), 'South': np.array([0, -1]), 'West': np.array([-1, 0])}
    center_x_y = [np.array([0, 0]) for _ in range(len(df))]
    for index, row in df.iterrows():
        G.add_node(index)
        for col_name in df.columns[0:4]:
            if pd.notna(row[col_name]):
                G.add_edge(index, int(row[col_name]), direction=col_name)                 
    
    queue = collections.deque([1])
    visited = {1}
    while queue:
        u = queue.popleft()
        for v in G.neighbors(u):
            if v not in visited:
                direction = G[u][v]['direction']
                center_x_y[v-1] = center_x_y[u-1] + dir_map[direction]
                #print(f"{v}: {center_x_y[v-1]} by {u}")
                visited.add(v)
                queue.append(v) 
    #print(center_x_y)
    pos = {i + 1: (p[0] * SPACE, p[1] * SPACE) for i, p in enumerate(center_x_y)}
    #print(pos)
    return G, pos

if  __name__ == "__main__":
    GenMap()