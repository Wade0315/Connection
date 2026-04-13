import re
import os
import networkx as nx
import subprocess
import logging
import threading
import queue

dir_map = {'north': 0, 'east': 1, 'south': 2, 'west': 3}

log = logging.getLogger(__name__)


def Parse(maze_file: str, status: dict, decision_queue: queue.Queue, Treasure: list):
    process = subprocess.Popen(["./execute"], stdin = subprocess.PIPE, stdout = subprocess.PIPE, text = True, bufsize = 1)

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
            log.debug("python end")
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
            log.debug("python start")
        
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
            pathIdx = []

    

    #read stdout deal with stdin
    for line_str in iter(process.stdout.readline, ''):
        line = line_str #include \n
        line_str = line_str.rstrip("\n")
        if "Do you want to load a file?[Y/N]:" in line_str:
            process.stdin.write("Y\n")
            process.stdin.flush()
        elif "Please input the file name:" in line_str:
            process.stdin.write(f"{maze_file}\n")
            process.stdin.flush()
        elif "Please enter \"startPoint\" , \"total cost limit\"" in line_str:
            process.stdin.write(f"{status["current_node"]} {status["time_left"]}\n")
            process.stdin.flush()
            log.info(f"enter startPoint: {status["current_node"]}, time_left: {status["time_left"]}")
        elif "Do you want to restart [Y/N]:" in line_str:
            if decision_queue is not None:
                res_d = decision_queue.get()
                log.info(f'get decision: {res_d}')
            process.stdin.write(f"{res_d}\n")
            process.stdin.flush()
        elif "Reach end [Y/N]:" in line_str:
            if status["current_node"] in Treasure:
                res_t = "Y"
            else:
                res_t = "N"
            process.stdin.write(f"{res_t}\n")
            process.stdin.flush()
            log.info(f"Reach end: {res_t}")

        elif "[message] There is no remain treasure point on the map. Mission completed" in line_str:
            log.info("\n\n===============Mission completed=================\n")

        elif not start and line_str != 'Graph start':
            log.debug(line_str) 

        res_v = ReadVertexs()
        if res_v: yield res_v
        res_p = ReadPath()
        if res_p: yield res_p


    #print(Paths)




if __name__ == "__main__":
    process = subprocess.Popen(['execute'], stdout = subprocess.PIPE, text = True, bufsize = 1)
    for data_type, data in Parse(process):
        if data_type == "GRAPH":
            log.debug('read graph!')
        elif data_type == "PATH":
            log.debug(f'path: {data}')



