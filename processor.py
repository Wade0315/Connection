from hm10_esp32 import HM10ESP32Bridge
from score import ScoreboardServer, ScoreboardFake

import time
import sys
import threading
import _thread
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
def action_processor(bridge: HM10ESP32Bridge, status: dict, event_queue: queue.Queue, path_queue: queue.Queue, restart_decision: threading.Event, ignore_event: threading.Event):
    global ingame
    log.info('[Action] - waiting for action')
    def initial_command():
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

    while True:
        action = event_queue.get() 
        log.debug(f"[Action] - Get action: {action}")
        if action == "ready":
            bridge.send(f'{action}\n')
            log.info(f"send {action}")
            ingame = True
            initial_command()
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
            if Passed_path:
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
            log.info("[Action] - have clear all action, start restart")      
            restart_decision.set()
        elif action == "go":            
            restart_decision.set()
            time.sleep(0.08)
            bridge.send()
            initial_command()
            ignore_event.clear()    
            log.info("restart go!")



            

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
def gen_path_processor(path_queue: queue.Queue, maze_file: str, status: dict, restart_decision: threading.Event):
    log.info('[Path] - generating path')
    Graph = []
    Treasure = []
    received = Parse(maze_file, status, restart_decision)
    for data_type, data in received:
        if data_type == "GRAPH":
            Graph = data
            log.debug("[Path] - read graph!")
        elif data_type == "TREASURE":
            Treasure = data
        elif data_type == "PATH":
            Path_json = []
            Path_list = []
            for i in data:
                json_dict = {
                    "NODE": i[0],
                    "MOVE": mapping_move.get(i[1])
                }
                Path_json.append(json_dict)
                Path_list.append((i[0], mapping_move.get(i[1])))
                path_queue.put((i[0], mapping_move.get(i[1])))
            json_str_buf = json.dumps(Path_list)
            log.debug(f"[Path] - Path data: {json_str_buf}")
            #log.debug(f"[Path] - Path data: {Path_list}")




def current_status_handler(status: dict, startPoint: int, limit: float, start_time: float):
    output_time = start_time
    if "end_time" not in status:
        status["end_time"] = start_time + limit
    while True:
        if status["time_left"] <= 1e-2:
            log.debug("break")
            _thread.interrupt_main()
            break
        Image_path = Passed_path[:]
        if not Image_path:
            status["current_node"] = startPoint
            status["step"] = 1
        else:
            status["current_node"] = Image_path[-1]
            status["step"] = len(Image_path)
            
        cost_time = status["end_time"] - time.time()
        status["time_left"] = cost_time
        if time.time() - output_time >= 5:
            log.debug(f"[STATUS] - current_node: {status['current_node']}, step: {status['step']}, time_left: {status['time_left']}")
            output_time = time.time()
        time.sleep(0.2)