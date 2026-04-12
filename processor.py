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

#處理即時資訊
def action_processor(bridge: HM10ESP32Bridge, event_queue: queue.Queue, path_queue: queue.Queue, decision_queue: queue.Queue):
    log.info('waiting for action')
    while True:
        action = event_queue.get() 
        log.debug(f"Get movement: {action}")
        if action == "ready":
            start = True
            # curIndex = 0
            # bridge.send(f'{movement_buffer[curIndex]}\n{movement_buffer[curIndex+1]}\n{movement_buffer[curIndex+1]}\n')  
            # curIndex += 2 
            output_str = ""
            if path_queue.qsize() < 3 and path_queue.qsize >= 0:
                for i in range(path_queue.qsize()):
                    output_str += f"{path_queue.get()}/n"
                bridge.send(output_str)
            elif path_queue.qsize >= 3:
                output_str = f"{path_queue.get()}/n{path_queue.get()}/n{path_queue.get()}/n"
                bridge.send(output_str)
            else:
                pass
        elif action == "NODELEAVE" and start:
            #curIndex += 1
            try:
                item = path_queue.get(block=False)
                bridge.send(f'{item}/n')
            except path_queue.empty():
                pass
        elif action == "restart":
            log.warning("need restart!")
            decision_queue.put("Y")
        elif action == "reach":
            log.info("reach treasure point!")
            decision_queue.put("N")

            

#connect to server
def score_processor(uid_queue: queue.Queue, scoreboard: ScoreboardServer):
    log.info('waiting for UID')
    while True:
        uid = uid_queue.get() 
        log.debug(f"Get uid: {uid}")
        
        score, time_remaining = scoreboard.add_UID(uid)
        current_score = scoreboard.get_current_score()
        
        log.info(f"Current score: {current_score}")

#store path 
def gen_path_processor(path_queue: queue.Queue, maze_file: str, startPoint: int, total_cost_limit: int, decision_queue: queue.Queue):
    log.info('generating path')
    received = Parse(maze_file, startPoint, total_cost_limit, decision_queue)
    for data_type, data in received:
        if data_type == "GRAPH":
            Graph = data
            log.debug("read graph!")
        elif data_type == "PATH":
            Path_list = []
            for i in data:
                json_dict = {
                    "NODE": i[0],
                    "MOVE": mapping_move.get(i[1])
                }
                Path_list.append(json_dict)
                json_str = json.dumps(json_dict)
                path_queue.put(json_str)
            json_str_buf = json.dumps(Path_list)
            log.debug(f"Path data: {json_str_buf}")
            #path_queue.put(json_str_buf)




