import subprocess
import os
from stdoutParser import Parse          #test in this file

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXEC_PATH = os.path.join(CURRENT_DIR, 'execute')


mapping_move = {'Forward': 'f', 'Turn-Right': 'r', 'Turn-Left': 'l', 'U-Turn': 'b'}

def commute():
    Graph = []
    Node = []
    Movement = []
    received = Parse()
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