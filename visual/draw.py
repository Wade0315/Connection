import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches  
import numpy as np
from MapLayout import GenMap
from getPath import getPath

ratio = 1
def drawGraph():
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
    nodes = nx.draw_networkx_nodes(G, pos, node_size=630*ratio, node_color='lightblue', edgecolors='navy', linewidths=0.8)
    edges = nx.draw_networkx_edges(G, pos, arrowstyle='-', arrowsize=10*ratio, edge_color='navy', connectionstyle='arc3,rad=0', node_size=630*ratio)
    labels = nx.draw_networkx_labels(G, pos, labels = node_labels, font_size=9)
    nodes.set_zorder(5)    
    for edge in edges: edge.set_zorder(1)   
    for t in labels.values(): t.set_zorder(15) # 手動設定    
    plt.axis('off')
    plt.savefig('static_graph.png', dpi=300, bbox_inches='tight')
    return fig, ax

#animation
def path_animation(file):
    G, pos = GenMap()
    fig, ax = drawGraph()
    path = getPath(file)

    path_dot = ax.scatter([], [], color='violet', s=630*ratio, zorder=7, label='Current Position', edgecolors='navy', linewidths=0.8, alpha = 0.8)
    path_line, = ax.plot([], [], color='violet', linewidth=4, zorder=3, alpha = 0.8)
    passed_line, = ax.plot([], [], color='gray', linewidth=2, zorder=2, alpha = 0.8)

    ax.axis('off')
    title_text = ax.set_title("Path Animation: Step 0")

    def get_line(p0, p2, num_points=21):
        p0, p2 = np.array(p0), np.array(p2)
        return np.linspace(p0, p2, num_points)
    
    path_points = []
    for i in range(len(path)-1):
        u, v = path[i], path[i+1]
        segment = get_line(pos[u], pos[v])
        if i == 0:
            path_points.extend(segment)
        else:
            path_points.extend(segment[1:])

    nav_arrow = patches.FancyArrowPatch(
        (0, 0), (0, 0), 
        color='violet',           
        zorder=3, 
        arrowstyle='-|>',       
        mutation_scale=20 * ratio 
    )
    ax.add_patch(nav_arrow)
    last_u_vec = np.array([0.0, 1.0])
    
    all_plots = []  #node
    all_path_points = np.array(path_points) #line
    def update(frame):
        nonlocal last_u_vec
        #update node
        eff_frame = min(frame, len(all_path_points)-1)
        plot_idx = eff_frame // 20
        current_node = path[plot_idx]
        current_pos = pos[current_node]
        all_plots.append(current_pos)
        path_dot.set_offsets(np.array(all_plots))

        #update line
        tail_length = 10 
        start_idx = max(0, eff_frame - tail_length)
        current_line_coords = all_path_points[start_idx : eff_frame+1]
        full_line_coords = all_path_points[0 : eff_frame+1]
        path_line.set_data(current_line_coords[:, 0], current_line_coords[:, 1])
        passed_line.set_data(full_line_coords[:, 0], full_line_coords[:, 1])

        #arrow (direction)
        if eff_frame > 0 and eff_frame % 20 != 0:
            prev_pos = all_path_points[eff_frame - 1]
            vec = current_pos - prev_pos
            dist = np.linalg.norm(vec)
            if dist > 1e-5: 
                last_u_vec = vec / dist 
            nav_arrow.set_alpha(1.0)       
        else:
            nav_arrow.set_alpha(0.0)
        arrow_len = 0.8 * ratio
        head_pos = all_path_points[eff_frame] + last_u_vec * arrow_len
        nav_arrow.set_positions(all_path_points[eff_frame], head_pos)

        changed_artists = [path_dot, path_line, passed_line, nav_arrow]

        if eff_frame % 20 == 0:    
            title_text.set_text(f"Path Animation: Step {plot_idx} (Node: {current_node})")
            changed_artists.append(title_text) 

        return changed_artists

    ani = animation.FuncAnimation(
        fig, update, frames=len(all_path_points)+30, interval=33, blit=True, repeat=False
    )

    writer = animation.FFMpegWriter(fps=30, bitrate=1800)

    ani.save('path_animation.mp4', writer=writer)


if __name__ == "__main__":
    drawGraph()
    FILE = "../data/medium_maze.csv"
    path_animation(FILE)

