from hm10_esp32 import HM10ESP32Bridge
from score import ScoreboardServer, ScoreboardFake

import time
import sys
import threading
import os
import re
import queue
import logging
import json
from Parser import Parse

log = logging.getLogger(__name__)


mapping_move = {'Forward': 'f', 'Turn-Right': 'r', 'Turn-Left': 'l', 'U-Turn': 'b'}
Passed_path = []
send_buffer = []
send_idx = 0
ingame = False


#處理即時資訊
def action_processor(bridge: HM10ESP32Bridge, status: dict, event_queue: queue.Queue, path_queue: queue.Queue, restart_decision: threading.Event, ignore_event: threading.Event):
    global ingame, Passed_path, send_buffer, send_idx
    log.info('[Action] - waiting for action')
    def initial_command():
        output_str = ""
        if path_queue.qsize() < 3 and path_queue.qsize() >= 0:
            for i in range(path_queue.qsize()):
                single_action = path_queue.get()
                output_str += f"{single_action[1]}\n"
                send_buffer.append(single_action[0])
            bridge.send(output_str)
            Passed_path.append(status["current_node"])
            log.debug(Passed_path)
            log.info(output_str.replace('\n', ' '))
        elif path_queue.qsize() >= 3:
            for i in range(3):
                single_action = path_queue.get()
                output_str += f"{single_action[1]}\n"
                send_buffer.append(single_action[0])
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
        elif (action == "NN" or action == "reach") and ingame:
            try:
                item = path_queue.get(block=False)
                bridge.send(f'{item[1]}\n')
                send_buffer.append(item[0])
                Passed_path.append(send_buffer[send_idx])
                send_idx += 1
                log.info(f"[Action] - send command: {item[1]}")
                log.debug(f"Passed_path: {Passed_path}")
            except queue.Empty:
                Passed_path.append(send_buffer[send_idx])
                if send_idx < len(send_buffer) - 1: send_idx += 1
                log.debug(f"Passed_path: {Passed_path}")
                pass




            

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
    received = Parse(maze_file, status, restart_decision)
    Path_idx = []
    for data_type, data in received:
        if data_type == "GRAPH":
            log.debug("[Path] - read graph!")
        elif data_type == "PATH":
            Path_idx.extend(data)
    
    Path_list = []
    for i in Path_idx:
        Path_list.append((i[0], mapping_move.get(i[1])))
        path_queue.put((i[0], mapping_move.get(i[1])))
    log.debug(f"[Path] - Path data: {Path_list}")




def current_status_handler(status: dict, startPoint: int, limit: float, start_time: float):
    output_time = start_time
    if "end_time" not in status:
        status["end_time"] = start_time + limit
    while True:
        if status["time_left"] <= 1e-2:
            log.debug("break")
            os._exit(0)
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
        if time.time() - output_time >= 1:
            log.debug(f"[STATUS] - current_node: {status['current_node']}, step: {status['step']}, time_left: {status['time_left']:.3f}s")
            output_time = time.time()
        time.sleep(0.2)

