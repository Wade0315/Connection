from hm10_esp32 import HM10ESP32Bridge
from score import ScoreboardServer, ScoreboardFake

import time
import sys
import threading
import re
import queue
import logging
import json
from stdoutParser import Parse

log = logging.getLogger(__name__)


mapping_move = {'Forward': 'f', 'Turn-Right': 'r', 'Turn-Left': 'l', 'U-Turn': 'b'}
movement_buffer = ['r', 'b', 'f', 'b', 'l', 'b']
curIndex = 0
start = False
#TODO
def action_processor(bridge: HM10ESP32Bridge, event_queue: queue.Queue):
    while True:
        action = event_queue.get() 
        log.debug(f"Get movement: {action}")
        if action == "ready":
            start = True
            curIndex = 0
            bridge.send(f'{movement_buffer[curIndex]}\n{movement_buffer[curIndex+1]}\n{movement_buffer[curIndex+1]}\n')  
            curIndex += 2 
        elif action == "NODELEAVE" and start:
            curIndex += 1

#connect to server
def score_processor(uid_queue: queue.Queue, scoreboard: ScoreboardServer):
    while True:
        uid = uid_queue.get() 
        log.debug(f"Get uid: {uid}")
        
        score, time_remaining = scoreboard.add_UID(uid)
        current_score = scoreboard.get_current_score()
        
        log.info(f"Current score: {current_score}")


def gen_path_processor(path_queue: queue.Queue, maze_file: str, startPoint: int, total_cost_limit: int):
    received = Parse(maze_file, startPoint, total_cost_limit)
    for data_type, data in received:
        if data_type == "GRAPH":
            Graph = data
            log.debug("read graph!")
        elif data_type == "PATH":
            Path = []
            for i in data:
                json_dict = {
                    "NODE": i[0],
                    "MOVE": mapping_move.get(i[1])
                }
                Path.append(json_dict)
            json_str = json.dumps(Path)
            path_queue.put(json_str)
            log.debug(f"Path data: {json_str}")