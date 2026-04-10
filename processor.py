from hm10_esp32 import HM10ESP32Bridge
from score import ScoreboardServer, ScoreboardFake

import time
import sys
import threading
import re
import queue
import logging

log = logging.getLogger(__name__)


#placement_buffer, movement_buffer = commucation()
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
            print("You: ", end="", flush=True)

#connect to server
def score_processor(uid_queue: queue.Queue, scoreboard: ScoreboardServer):
    while True:
        uid = uid_queue.get() 
        log.debug(f"Get uid: {uid}")
        
        score, time_remaining = scoreboard.add_UID(uid)
        current_score = scoreboard.get_current_score()
        
        log.info(f"Current score: {current_score}")
        print("You: ", end="", flush=True)
