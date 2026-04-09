import re
import os
import networkx as nx
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXEC_PATH = os.path.join(CURRENT_DIR, 'execute')

dir_map = {'north': 0, 'east': 1, 'south': 2, 'west': 3}

def Execute_and_Parse(process: subprocess.Popen[str]):
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
            return ("GRAPH", Vertexs)
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
        
        return None

    def ReadPath():
        nonlocal line_str, readingPath, Paths, pathIdx
        if readingPath:
            if line_str == "Submission complete.":
                readingPath = False
                Paths.append(pathIdx)
                return ("PATH", pathIdx)
            
            raw_path_idx = re.search(r'\s*Step\s*\d+\s*:\s*\[Node\s*:\s*(\d+)\s*,\s*Facing\s*:\s*([a-zA-Z]+)\s*\]\s*->\s*Command:\s*([a-zA-Z-]+)\s*', line_str) 
            if raw_path_idx is not None:
                idx = int(raw_path_idx.group(1))
                dir = dir_map.get(raw_path_idx.group(2))
                movement = raw_path_idx.group(3)
                pathIdx.append([idx*4+dir, movement])
        
        if re.search(r'\[Mission #\d+\] Heading to target node:\s+\d+', line_str) and not readingPath:
            readingPath = True
            print("Hello")
            pathIdx = []

    

    #read stdout deal with stdin
    for line_str in iter(process.stdout.readline, ''):
        line = line_str #include \n
        line_str = line_str.rstrip("\n")
        if "Do you want to load a file?[Y/N]:" in line_str:
            res_check = input("Do you want to load a file?[Y/N]: ") or "Y"
            process.stdin.write(f"{res_check}\n")
            process.stdin.flush()
        elif "Please input the file name:" in line_str:
            res_file = input("Please input the file name: ") or "maze.csv"
            process.stdin.write(f"{res_file}\n")
            process.stdin.flush()
        elif "Please enter \"startPoint\" , \"total cost limit\"" in line_str:
            res_init = input("Please enter \"startPoint\" , \"total cost limit\": ") or "1 1000"
            res_init = [int(n) for n in res_init.split()]
            process.stdin.write(f"{res_init[0]} {res_init[1]}\n")
            process.stdin.flush()
        elif "Do you want to restart [Y/N]:" in line_str:
            res_restart = input("Do you want to restart [Y/N]: ") or "N"
            process.stdin.write(f"{res_restart}\n")
            process.stdin.flush()

        elif not start and line_str != 'Graph start':
            print(line, end = "")    

        res_v = ReadVertexs()
        if res_v: yield res_v
        res_p = ReadPath()
        if res_p: yield res_p


    #print(Paths)




if __name__ == "__main__":
    process = subprocess.Popen([EXEC_PATH], stdout = subprocess.PIPE, text = True, bufsize = 1)
    for data_type, data in Execute_and_Parse(process):
        if data_type == "GRAPH":
            print('read graph!')
        elif data_type == "PATH":
            print(f'path: {data}')



