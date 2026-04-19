import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from geometry import get_arc_midpoint
from geometry import get_arc_path

arc_value = 0.37
ratio = 1

def drawGraph(G, pos):

    x_coords = [p[0] for p in pos.values()]
    y_coords = [p[1] for p in pos.values()]
    
    span_x = max(x_coords) - min(x_coords)
    span_y = max(y_coords) - min(y_coords)
    
    fig_w = max(10, span_x * 0.3)
    fig_h = max(10, span_y * 0.3)
    
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))    
    ax.set_aspect('equal')

    treasure_nodes = []
    normal_nodes = []
    for node, data in G.nodes(data = True):
        treasure = data.get('score', 0)
        if treasure != 0:
            treasure_nodes.append(node)
        else :
            normal_nodes.append(node)
    nx.draw_networkx_nodes(G, pos, nodelist = normal_nodes, node_size=630*ratio, node_color='lightblue', edgecolors='navy', linewidths=0.8)
    nx.draw_networkx_nodes(G, pos, node_size=630*ratio, nodelist = treasure_nodes, node_color='lightgreen', edgecolors='navy', linewidths=0.8)

    # 畫出標籤 (節點名稱)
    node_labels = {}
    for node, data in G.nodes(data = True):
        score = data.get('score', 0)
        if score != 0:
            node_labels[node] = f"{node}\n\'{score}\'"
        else :
            node_labels[node] = f"{node}"

    plot_labels = nx.draw_networkx_labels(G, pos, labels = node_labels, font_size=9)
    for t in plot_labels.values(): t.set_zorder(15) # 手動設定    
    
    # 畫出邊 (箭頭)
    inter_edges = []
    intra_edges = []
    for u, v in G.edges():
        if abs(u - v) > 3: 
            inter_edges.append((u, v))
        else:
            intra_edges.append((u, v))

    intra_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True) if (u, v) in intra_edges}
    inter_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True) if (u, v) in inter_edges}

    nx.draw_networkx_edges(G, pos, edgelist=intra_edges, arrowstyle='->', arrowsize=10*ratio, edge_color='gray', connectionstyle='arc3,rad=0', node_size=630*ratio)
    for (u, v) in inter_edges:
        path = get_arc_path(pos[u], pos[v], -arc_value, 100)
        # path[:,0] 是 x 座標，path[:,1] 是 y 座標
        plt.plot(path[:,0], path[:,1], color='black', zorder=1)
        arrow_tail = path[88]  
        arrow_head = path[93]  
        ax.annotate('', 
                    xy=arrow_head,     # 箭頭尖端的位置
                    xytext=arrow_tail, # 箭頭尾巴的位置
                    arrowprops=dict(
                        arrowstyle="->",  # 實心箭頭樣式
                        color='black',      # 與線條同色
                        lw=1,            # 線條粗細
                        mutation_scale=15*ratio  # 箭頭大小 (數值越大箭頭越明顯)
                    ),
                    zorder=2) # 讓箭頭稍微浮在線條上方
    
    intra_text = nx.draw_networkx_edge_labels(
        G, pos, 
        edge_labels=intra_labels, 
        label_pos=0.5, 
        rotate=False, 
        font_size=4,
        bbox=dict(boxstyle='circle, pad = 0.2', facecolor='white', edgecolor='none', alpha=0.3), 
        horizontalalignment='center',
        verticalalignment='center',
    )
    for t in intra_text.values():
        t.set_zorder(2)

    inter_label_objects = {}
    for u, v in inter_edges:
        points = get_arc_path(pos[u], pos[v], rad= -arc_value, num_points=21)
        mid_x, mid_y = points[8] 
        
        t = ax.text(
            mid_x, mid_y, 
            str(inter_labels[(u, v)]),
            fontsize=6, color='black', weight='bold',
            bbox=dict(boxstyle='circle, pad = 0.15', facecolor='white', alpha=0.8, edgecolor='black', linewidth = 1),
            ha='center', va='center', zorder=3
        )
        
        inter_label_objects[(u,v)] = t
    
    '''
    inter_text = nx.draw_networkx_edge_labels(
        G, pos, 
        edge_labels=inter_labels, 
        label_pos=0.2975, 
        rotate=False, 
        font_size=8,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.5, pad=0.2), 
        horizontalalignment='center',
        verticalalignment='center',
    )
    '''

    plt.axis('off')
    plt.savefig('static_graph.png', dpi=300, bbox_inches='tight')

    return fig, ax, inter_label_objects



def aniAlgo(G, pos, Paths):
    #animation

    fig, ax, inter_label_objects = drawGraph(G, pos)
    # 2. 建立一個「空的」或「初始位置」的 Scatter 物件，並將其指派給變數 path_dot
    # 動態更新的對象
    path_dot = ax.scatter([], [], color='violet', s=630*ratio, zorder=5, label='Current Position', edgecolors='navy', linewidths=0.8)

    # 保留走過的路徑線條，可以先建立一個空的 Line2D
    path_line, = ax.plot([], [], color='violet', linewidth=2, zorder=1)

    ax.axis('off')
    title_text = ax.set_title("Path Animation: Step 0")

    path = []
    for i in Paths:
        for idx in i:
            path.append(idx[0])
    
    path_points = []
    for i in range(len(path)-1):
        u, v = path[i], path[i+1]
        current_rad = -arc_value if abs(u-v) > 3 else 0
        segment = get_arc_path(pos[u], pos[v], rad = current_rad, num_points=21)
        if i == 0:
            path_points.extend(segment)
        else:
            path_points.extend(segment[1:])
    
    all_path_points = np.array(path_points)
    all_plots = []
    # 3. 定義更新函數
    def update(frame):
        eff_frame = min(frame, len(all_path_points)-1)
        plot_idx = eff_frame // 20
        current_node = path[plot_idx]
        next_node = path[plot_idx + 1] if plot_idx < len(path) - 1 else current_node
        new_pos = pos[current_node] # 取得 (x, y)
        all_plots.append(new_pos)

        # 更新路徑線段：直接抓取到目前幀為止的所有座標點
        current_line_coords = all_path_points[ :eff_frame+1]
        path_dot.set_offsets(np.array(all_plots))
        path_line.set_data(current_line_coords[:, 0], current_line_coords[:, 1])

        changed_artists = [path_dot, path_line]

        if eff_frame % 20 == 0:    
            # 更新標題
            title_text.set_text(f"Path Animation: Step {plot_idx} (Node: {current_node})")
            changed_artists.append(title_text) 

        #refresh label
        u = current_node
        v = next_node
        if (u, v) in inter_label_objects:
            target_label = inter_label_objects[(u, v)]
            if frame % 20 >= 8:
                # 改變背景顏色與文字顏色
                target_label.get_bbox_patch().set_facecolor('violet')
                target_label.get_bbox_patch().set_alpha(1.0)
                changed_artists.append(target_label) 
        return changed_artists
    # 4. 建立動畫
    # blit=True 代表只重繪改變的部分，效率最高
    ani = animation.FuncAnimation(
        fig, update, frames=len(all_path_points)+30, interval=33, blit=True, repeat=False
    )

    writer = animation.FFMpegWriter(fps=30, metadata=dict(artist='Me'), bitrate=1800
    , extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-threads', '0', '-preset', 'ultrafast'])

    # 儲存為 mp4
    ani.save('path_animation.mp4', writer=writer)

