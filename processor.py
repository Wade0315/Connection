from hm10_esp32 import HM10ESP32Bridge
from score import ScoreboardServer, ScoreboardFake

import time
import sys
import threading
import re
import queue
import logging
import json
from Parser import Parse

log = logging.getLogger(__name__)


mapping_move = {'Forward': 'f', 'Turn-Right': 'r', 'Turn-Left': 'l', 'U-Turn': 'b'}
Passed_path = []
ingame = False


#處理即時資訊
def action_processor(bridge: HM10ESP32Bridge, status: dict, event_queue: queue.Queue, path_queue: queue.Queue, decision_queue: queue.Queue, ignore_event: threading.Event):
    global ingame
    log.info('[Action] - waiting for action')
    while True:
        action = event_queue.get() 
        log.debug(f"[Action] - Get action: {action}")
        if action == "ready":
            bridge.send(f'{action}\n')
            ingame = True
            output_str = ""
            if path_queue.qsize() < 3 and path_queue.qsize() >= 0:
                for i in range(path_queue.qsize()):
                    output_str += f"{path_queue.get()[1]}\n"
                bridge.send(output_str)
                Passed_path.append(status["current_node"])
                log.info(output_str.replace('\n', ' '))
            elif path_queue.qsize() >= 3:
                output_str = f"{path_queue.get()[1]}\n{path_queue.get()[1]}\n{path_queue.get()[1]}\n"
                bridge.send(output_str)
                Passed_path.append(status["current_node"])
                log.info(output_str.replace('\n', ' '))
            else:
                log.error("path_queue error!")
                pass
        elif action == "NN" and ingame:
            try:
                item = path_queue.get(block=False)
                Passed_path.append(item[0])
                bridge.send(f'{item[1]}\n')
                log.info(f"[Action] - send command: {item[1]}")
                log.debug(f"Passed_path: {Passed_path}")
            except queue.Empty:
                pass
        elif action == "reach" and ingame:
            log.info("[Action] - reach treasure point!")
            try:
                item = path_queue.get(block=False)
                Passed_path.append(item[0])
                bridge.send(f'{item[1]}\n')
                log.info(f"[Action] - send command: {item[1]}")
                log.debug(f"Passed_path: {Passed_path}")
            except queue.Empty:
                pass
        elif action == "restart" and ingame:
            log.warning("[Action] - need restart!")
            ignore_event.set()
            Passed_path.pop()
            while not event_queue.empty():
                try: event_queue.get_nowait()
                except queue.Empty: break            
            while not path_queue.empty():
                try: path_queue.get_nowait()
                except queue.Empty: break  
            time.sleep(0.2)
            #保險
            while not event_queue.empty():
                try: event_queue.get_nowait()
                except queue.Empty: break
            log.info("[ACtion] - have clear all action, start restart")      
            decision_queue.put("Y")
        elif action == "go":
            log.info("restart go!")
            ignore_event.clear()    



            

#connect to server
def score_processor(uid_queue: queue.Queue, scoreboard: ScoreboardServer, status: dict):
    log.info('[Score] - waiting for UID')
    while True:
        uid = uid_queue.get() 
        log.debug(f"[Score] - Get uid: {uid}")
        
        score, time_remaining = scoreboard.add_UID(uid)
        if time_remaining > 0 and abs(time_remaining - status["time_left"]) >= 1:
            status["end_time"] = time_remaining + time.time()
        current_score = scoreboard.get_current_score()
        
        log.info(f"[Score] - Current score: {current_score}")
        time.sleep(0.5)

#store path 
def gen_path_processor(path_queue: queue.Queue, maze_file: str, status: dict, decision_queue: queue.Queue):
    log.info('[Path] - generating path')
    Graph = []
    Treasure = []
    received = Parse(maze_file, status, decision_queue)
    for data_type, data in received:
        if data_type == "GRAPH":
            Graph = data
            log.debug("[Path] - read graph!")
        elif data_type == "TREASURE":
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
            log.debug(f"[Path] - Path data: {json_str_buf}")
            #path_queue.put(json_str_buf)




def current_status_handler(status: dict, startPoint: int, limit: float, start_time: float):
    if "end_time" not in status:
        status["end_time"] = start_time + limit
    while True:
        Image_path = Passed_path[:]
        if not Image_path:
            status["current_node"] = startPoint
            status["step"] = 1
        else:
            status["current_node"] = Image_path[-1]
            status["step"] = len(Image_path)
        cost_time = status["end_time"] - time.time()
        if cost_time >= 0:
            status["time_left"] = cost_time
        else:
            status["time_left"] = 0
            break
        log.debug(f"[STATUS] - current_node: {status['current_node']}, step: {status['step']}, time_left: {status['time_left']}")
        time.sleep(1)