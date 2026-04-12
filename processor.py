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
Passed_path = []
# movement_buffer = ['r', 'b', 'f', 'b', 'l', 'b']
# curIndex = 0
ingame = False

#TODO

#處理即時資訊
def action_processor(bridge: HM10ESP32Bridge, event_queue: queue.Queue, path_queue: queue.Queue, decision_queue: queue.Queue):
    global ingame
    log.info('waiting for action')
    while True:
        action = event_queue.get() 
        log.debug(f"Get movement: {action}")
        if action == "ready":
            ingame = True
            # curIndex = 0
            # bridge.send(f'{movement_buffer[curIndex]}\n{movement_buffer[curIndex+1]}\n{movement_buffer[curIndex+1]}\n')  
            # curIndex += 2 
            output_str = ""
            if path_queue.qsize() < 3 and path_queue.qsize() >= 0:
                for i in range(path_queue.qsize()):
                    output_str += f"{path_queue.get()[1]}\n"
                bridge.send(output_str)
            elif path_queue.qsize() >= 3:
                output_str = f"{path_queue.get()[1]}\n{path_queue.get()[1]}\n{path_queue.get()[1]}\n"
                bridge.send(output_str)
            else:
                pass
        elif action == "NODELEAVE" and ingame:
            #curIndex += 1
            try:
                item = path_queue.get(block=False)
                Passed_path.append(item[0])
                bridge.send(f'{item[1]}\n')
            except queue.Empty:
                pass
        elif action == "restart":
            log.warning("need restart!")
            with path_queue.mutex:
                path_queue.queue.clear()
            with event_queue.mutex:
                event_queue.queue.clear()
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
        time.sleep(0.5)

#store path 
def gen_path_processor(path_queue: queue.Queue, maze_file: str, restrain: dict, decision_queue: queue.Queue):
    log.info('generating path')
    Graph = []
    Treasure = []
    received = Parse(maze_file, restrain, decision_queue, Passed_path, Treasure)
    for data_type, data in received:
        if data_type == "GRAPH":
            Graph = data
            log.debug("read graph!")
        elif data_type == "TREASURE":
            #TODO get treasure
            Treasure = data
        elif data_type == "PATH":
            Path_list = []
            for i in data:
                json_dict = {
                    "NODE": i[0],
                    "MOVE": mapping_move.get(i[1])
                }
                Path_list.append(json_dict)
                path_queue.put((i[0], mapping_move.get(i[1])))
            json_str_buf = json.dumps(Path_list)
            log.debug(f"Path data: {json_str_buf}")
            #path_queue.put(json_str_buf)




def current_status_handler(restrain: dict, startPoint: int, limit: float, current_time: float):
    while True:
        if not Passed_path:
            restrain["startPoint"] = startPoint
        else:
            restrain["startPoint"] = Passed_path[-1] or startPoint
        cost_time = (time.time() - current_time)
        if cost_time >= 0:
            restrain["limit"] = limit - (time.time() - current_time)
        else:
            restrain["limit"] = 0
        log.debug(f" [STATUS] - startPoint: {restrain['startPoint']}, limit: {restrain['limit']}")
        time.sleep(1)