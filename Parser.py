import re
import os
import networkx as nx
import subprocess
import logging
import threading
import queue

dir_map = {'north': 0, 'east': 1, 'south': 2, 'west': 3}

log = logging.getLogger(__name__)


def Parse(maze_file: str, status: dict):
    process = subprocess.Popen(["./execute"], stdin = subprocess.PIPE, stdout = subprocess.PIPE, text = True, bufsize = 1)
    start = False
    Paths = []
    readingPath = False
    pathIdx = []
    what_Mission = 0
    is_initial_start = True

    def ReadPath():
        nonlocal line_str, readingPath, Paths, pathIdx, what_Mission, is_initial_start
        if readingPath:
            if line_str == "Submission complete.":
                readingPath = False
                Paths.extend(pathIdx)
            
            raw_path_idx = re.search(r'\s*Step\s*(\d+)\s*:\s*\[Node\s*:\s*(\d+)\s*,\s*Facing\s*:\s*([a-zA-Z]+)\s*\]\s*->\s*Command:\s*([a-zA-Z-]+)\s*', line_str) 
            if raw_path_idx is not None:
                step = int(raw_path_idx.group(1))
                idx = int(raw_path_idx.group(2))
                dir = dir_map.get(raw_path_idx.group(3))
                movement = raw_path_idx.group(4)
                if is_initial_start:
                    is_initial_start = False
                else:
                    pathIdx.append([idx, movement])
        
        startMission = re.search(r'\[Mission #(\d+)\] Heading to target node:\s+\d+', line_str)
        if startMission and not readingPath:
            readingPath = True
            what_Mission = int(startMission.group(1))
            pathIdx = []    
            log.debug("read")

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
            process.stdin.write(f"{status["current_node"]} {status["time_left"]*1000}\n")
            process.stdin.flush()
            log.info(f"enter startPoint: {status["current_node"]}, time_left: {status["time_left"]}")
        elif "[message] There is no remain treasure point on the map. Mission completed" in line_str:
            yield("PATH", Paths)
            Paths = []
            log.info("\n=============== Gen path completed =================\n")

        elif not start and line_str != 'Graph start':
            log.debug(line_str) 

        ReadPath()
            






if __name__ == "__main__":
    MAZE_FILE = "data/big_maze_114.csv"
    status = {"current_node": 25, "step": 1, "time_left": 65000}
    restart_decision = threading.Event()
    for data_type, data in Parse(MAZE_FILE, status, restart_decision):
        if data_type == "GRAPH":
            log.debug('read graph!')
        elif data_type == "PATH":
            log.debug(f'path: {data}')



