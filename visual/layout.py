import networkx as nx

def Layout(Vertexs):
    relative_dir = []
    for vertex in Vertexs:
        for edge in vertex[4:]:
            if Vertexs[edge[1]][0] > vertex[0]:
                relative_dir.append([vertex[0], Vertexs[edge[1]][0], vertex[1]])


    center_x = [0 for _ in range(len(Vertexs))]
    center_y = [0 for _ in range(len(Vertexs))]

    G = nx.DiGraph()
    pos = {}
    GROUP_SPACING = 10
    delta = 3

    for vertex in Vertexs:
        OriIdx = vertex[0]
        dir = vertex[1]
        RealIdx = vertex[2]
        score_value = vertex[3]
        G.add_node(RealIdx, direction = dir, group = OriIdx, score = score_value)

        #找是否有相鄰的邊，更新那個大點的center
        for r_dir in relative_dir:
            if OriIdx == r_dir[0]:
                if r_dir[2] == 0:
                    center_x[r_dir[1]] = center_x[OriIdx]
                    center_y[r_dir[1]] = center_y[OriIdx] + GROUP_SPACING
                elif r_dir[2] == 1:
                    center_x[r_dir[1]] = center_x[OriIdx] + GROUP_SPACING
                    center_y[r_dir[1]] = center_y[OriIdx]
                elif r_dir[2] == 2:
                    center_x[r_dir[1]] = center_x[OriIdx]
                    center_y[r_dir[1]] = center_y[OriIdx] - GROUP_SPACING
                elif r_dir[2] == 3:
                    center_x[r_dir[1]] = center_x[OriIdx] - GROUP_SPACING
                    center_y[r_dir[1]] = center_y[OriIdx] 

        #決定小點的位置
        if dir == 0:
            pos[RealIdx] = (center_x[OriIdx], center_y[OriIdx] + delta)
        elif dir == 1:
            pos[RealIdx] = (center_x[OriIdx] + delta, center_y[OriIdx])
        elif dir == 2:
            pos[RealIdx] = (center_x[OriIdx], center_y[OriIdx] - delta)
        elif dir == 3:
            pos[RealIdx] = (center_x[OriIdx] - delta, center_y[OriIdx])

        for edge in vertex[4:]:
            G.add_edge(RealIdx, edge[1], weight = edge[0]) 
    return G, pos