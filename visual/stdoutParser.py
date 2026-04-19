import subprocess
import re
import networkx as nx

def Execute_and_Parse(dir_map):

    process = subprocess.Popen(['./a.out'], stdout = subprocess.PIPE, text = True, bufsize = 1)
    start = False
    Vertexs_string = []
    vertex = ""
    Paths = []
    readingPath = False
    pathIdx = []

    def ReadVertexs():
        nonlocal start, line_str, Vertexs_string, vertex
        if line_str == 'Graph end':
            start = False
            print("python end")
        if start:
            if line_str == "Vertex {":
                vertex = ""
            elif line_str == "}":
                Vertexs_string.append(vertex)
            else:
                vertex += line_str 
        
        if line_str == 'Graph start':
            start = True
            print("python start")

    def ReadPath():
        nonlocal line_str, readingPath, Paths, pathIdx
        if readingPath:
            if line_str == "Submission complete.":
                readingPath = False
                Paths.append(pathIdx)
            
            raw_path_idx = re.search(r'\s*Step\s+\d+: \[Node\s*(\d+), Facing\s+([a-zA-Z]+)\]', line_str) 
            raw_path_mv = re.search(r' -> Command:\s+([a-zA-Z-]+)', line_str)
            if raw_path_idx is not None:
                idx = int(raw_path_idx.group(1))
                dir = dir_map.get(raw_path_idx.group(2))
                if raw_path_mv is not None:
                    movement = raw_path_mv.group(1)
                else :
                    movement = ""
                pathIdx.append([idx*4+dir, movement])
        
        if re.search(r'\[Mission #\d+\] Heading to target node:\s+\d+', line_str) and not readingPath:
            readingPath = True
            pathIdx = []


    #read stdout 
    for line_str in iter(process.stdout.readline, ''):
        line = line_str #include \n
        line_str = line_str.rstrip("\n")
        if not start and line_str != 'Graph start':
            print(line, end = "")    

        ReadVertexs()
        ReadPath()

    #print(Paths)
    Vertexs = []
    for element in Vertexs_string:
        OriIdx = int(re.search(r'OriIdx:\s*(\d+)', element).group(1))
        dir = int(re.search(r'dir:\s*(\d+)', element).group(1))
        RealIdx = int(re.search(r'RealIdx:\s*(\d+)', element).group(1))
        score = int(re.search(r'score:\s*(\d+)', element).group(1))
        edges = []
        for w, t in re.findall(r'weight\s*:\s*(\d+),\s*terminal\s*:\s*(\d+)', element):
            edges.append([int(w), int(t)])
        Vertexs.append([OriIdx, dir, RealIdx, score] + edges)


    return Vertexs, Paths






