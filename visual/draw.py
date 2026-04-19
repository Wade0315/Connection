import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from MapLayout import GenMap

ratio = 1
def static_graph():
    G, pos = GenMap()
    x_coords = [p[0] for p in pos.values()]
    y_coords = [p[1] for p in pos.values()]
    
    span_x = max(x_coords) - min(x_coords)
    span_y = max(y_coords) - min(y_coords)
    
    fig_w = max(10, span_x * 0.3)
    fig_h = max(10, span_y * 0.3)

    node_labels = {n: str(n) for n in G.nodes()} 
    
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))   
    ax.set_aspect('equal')
    nx.draw_networkx_nodes(G, pos, node_size=630*ratio, node_color='lightblue', edgecolors='navy', linewidths=0.8)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=10*ratio, edge_color='gray', connectionstyle='arc3,rad=0', node_size=630*ratio)
    nx.draw_networkx_labels(G, pos, labels = node_labels, font_size=9)
    plt.axis('off')
    plt.savefig('static_graph.png', dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    static_graph()

