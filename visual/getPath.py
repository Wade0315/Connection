import re
import os
import networkx as nx
import subprocess
import logging
import threading
import queue

dir_map = {'north': 0, 'east': 1, 'south': 2, 'west': 3}
mapping_move = {'Forward': 'f', 'Turn-Right': 'r', 'Turn-Left': 'l', 'U-Turn': 'b'}



def getPath(maze_file: str):
    process = subprocess.Popen(["../visual_execute"], stdin = subprocess.PIPE, stdout = subprocess.PIPE, text = True, bufsize = 1)
    start = False
    Paths = []
    readingPath = False
    pathIdx = []
    last_node = 0
    path_cost = 0
    cumulate_cost = {}

    def ReadPath():
        nonlocal line_str, readingPath, Paths, pathIdx, last_node, path_cost, cumulate_cost
        if readingPath:
            if line_str == "Submission complete.":
                readingPath = False
                Paths.extend(pathIdx)
                cumulate_cost[pathIdx[-1]] =  path_cost
                #print(cumulate_cost)
            raw_path_idx = re.search(r'\s*Step\s*(\d+)\s*:\s*\[Node\s*:\s*(\d+)\s*,\s*Facing\s*:\s*([a-zA-Z]+)\s*\]', line_str) 
            if raw_path_idx is not None:
                step = int(raw_path_idx.group(1))
                idx = int(raw_path_idx.group(2))
                dir = dir_map.get(raw_path_idx.group(3))
                if last_node == idx:
                    pass
                else:
                    pathIdx.append(idx)
                    last_node = idx
        
        startMission = re.search(r'\[Mission #(\d+)\] Heading to target node:\s+\d+,\s*cumulate cost:\s*(\d+\.\d+)', line_str)
        if startMission and not readingPath:
            path_cost = float(startMission.group(2))
            readingPath = True
            pathIdx = []    

    #read stdout deal with stdin
    for line_str in iter(process.stdout.readline, ''):
        line_str = line_str.rstrip("\n")
        if "Do you want to load a file?[Y/N]:" in line_str:
            process.stdin.write("Y\n")
            process.stdin.flush()
        elif "Please input the file name:" in line_str:
            process.stdin.write(f"{maze_file}\n")
            process.stdin.flush()
        elif "Please enter \"startPoint\" , \"total cost limit\"" in line_str:
            process.stdin.write(f"25 65000\n")
            process.stdin.flush()
        elif "[message] There is no remain treasure point on the map. Mission completed" in line_str:
            return Paths, cumulate_cost
        elif "Do you want to restart [Y/N]:" in line_str:
            process.stdin.write(f"N\n")
            process.stdin.flush()
        ReadPath()
            

if __name__ == "__main__":
    FILE = "../data/big_maze_114.csv"
    print(getPath(FILE))


