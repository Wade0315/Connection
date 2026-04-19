import pandas as pd
import networkx as nx

FILE = "../data/medium_maze.csv"
def GenMap() :
    df = pd.read_csv(FILE, index_col='index')
    G = nx.DiGraph()
    for index, row in df.iterrows():
        G.add_node(index)
        for col_name in df.columns[0:4]:
            if pd.notna(row[col_name]) and int(row[col_name]) > index:
                G.add_edge(index, int(row[col_name])) 
                print(f"{index}, {row[col_name]}")


GenMap()