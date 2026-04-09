import subprocess
import os
#from stdoutParser import Execute_and_Parse          #test in this file
from .stdoutParser import Execute_and_Parse        #test in outer main.py

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXEC_PATH = os.path.join(CURRENT_DIR, 'execute')


mapping_move = {'Forward': 'f', 'Turn-Right': 'r', 'Turn-Left': 'l', 'U-Turn': 'b'}

def commute():
    process = subprocess.Popen([EXEC_PATH], stdin = subprocess.PIPE, stdout = subprocess.PIPE, text = True, bufsize = 1)
    Graph = []
    Node = []
    Movement = []
    received = Execute_and_Parse(process)
    for data_type, data in received:
        if data_type == "GRAPH":
            Graph = data
            yield ("GRAPH", Graph)
        elif data_type == "PATH":
            Node.extend([i[0] for i in data])
            Movement.extend([mapping_move.get(i[1]) for i in data])
            yield ("NODE", Node)
            yield ("MOVE", Movement)



if __name__ == "__main__":
    for data_type, data in commute():
        if data_type == "GRAPH":
            print(f'read graph!')
        elif data_type == "MOVE":
            print(f'MOVEMENT: {data}')
        elif data_type == "NODE":
            print(f'NODE: {data}')