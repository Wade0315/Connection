import argparse
import logging
import os
import sys
import time
from hm10_esp32 import HM10ESP32Bridge


import numpy as np
import pandas
# from BTinterface import BTInterface
from log import setup_logging

from score import ScoreboardServer, ScoreboardFake
import threading
import queue
#from chat_hm10_esp32 import hm10_main
import BT_setup
import processor
'''
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG,
    handlers=[
        logging.FileHandler("system.log", mode = 'w', encoding='utf-8')
        # logging.StreamHandler()
    ]
)
'''


setup_logging()
log = logging.getLogger(__name__)

# TODO : Fill in the following information
MAZE_FILE = "data/small_maze.csv"
STARTPOINT = 1
LIMIT = 10000
TEAM_NAME = "YOUR_TEAM_NAME"
SERVER_URL = "http://carcar.ntuee.org/scoreboard"
BT_PORT = ""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="0: treasure-hunting, 1: self-testing", type=str)
    parser.add_argument("--maze-file", default=MAZE_FILE, help="Maze file", type=str)
    parser.add_argument("--startPoint", default=STARTPOINT, help="startPoint", type=int)
    parser.add_argument("--limit", default=LIMIT, help="limit", type=int)
    parser.add_argument("--bt-port", default=BT_PORT, help="Bluetooth port", type=str)
    parser.add_argument(
        "--team-name", default=TEAM_NAME, help="Your team name", type=str
    )
    parser.add_argument("--server-url", default=SERVER_URL, help="Server URL", type=str)
    return parser.parse_args()



def main(mode: int, maze_file: str, startPoint: int, limit: int, bt_port: str, team_name: str, server_url: str):
    #point = ScoreboardServer(team_name, server_url)
    #point = ScoreboardFake("your team name", "data/fakeUID.csv") # for local testing
    
    bridge = HM10ESP32Bridge(port=BT_PORT)

    event_queue = queue.Queue() #store instant information
    path_queue = queue.Queue()  #store path 
    decision_queue = queue.Queue()  #eat the command if the car is gonna restart or continue
    uid_queue = queue.Queue()   #eat uid
    

    ### Bluetooth connection haven't been implemented yet, we will update ASAP ###
    # interface = BTInterface(port=bt_port)
    # TODO : Initialize necessary variables

    if mode == "0":
        log.info("Mode 0: For treasure-hunting")
        # TODO : for treasure-hunting, which encourages you to hunt as many scores as possible
        scoreboard = ScoreboardServer("Team3", "http://140.112.175.18")
        time.sleep(1)
        threading.Thread(target=processor.score_processor, args=(uid_queue, scoreboard), daemon=True).start()
        BT_setup.hm10_main(bridge)
        threading.Thread(target=processor.gen_path_processor, args=(path_queue,maze_file, startPoint, limit, decision_queue), daemon=True).start()
        threading.Thread(target=BT_setup.background_listener, args=(bridge,uid_queue, event_queue), daemon=True).start()
        threading.Thread(target=processor.action_processor, args=(bridge, event_queue, path_queue, decision_queue), daemon=True).start()

        try:
            while True:
                user_msg = input("You: ")
                if user_msg.lower() in ['exit', 'quit']: break
                if user_msg: 
                    bridge.send(f'{user_msg}\n')
                    log.info(f"user input: {user_msg}")
                    print("You: ", end="", flush=True)      
        except (KeyboardInterrupt, EOFError):
            pass
        print("\nChat closed.")

        

        
    elif mode == "1":
        log.info("Mode 1: test read map.")
        threading.Thread(target=processor.gen_path_processor, args=(path_queue,maze_file, startPoint, limit, decision_queue), daemon=True).start()
        threading.Thread(target=processor.action_processor, args=(bridge, event_queue, path_queue, decision_queue), daemon=True).start()
        while True:
            try:
                path_data = path_queue.get(timeout=1) 
                log.info(f"get path: {path_data}") 
                decision_queue.put("N")
            except queue.Empty:
                pass
            except KeyboardInterrupt:
                log.info("end test")
                break


    elif mode == "2": #crosstest
        log.info("Mode 1: cross test.")
        BT_setup.hm10_main(bridge)
        threading.Thread(target=BT_setup.background_listener, args=(bridge,event_queue, uid_queue), daemon=True).start()
        threading.Thread(target=processor.action_processor, args=(bridge, event_queue, path_queue, decision_queue), daemon=True).start()
        
        def auto_refill_path(path_queue: queue.Queue):
            test_moves = [(0, 'r'), (1, 'b'), (2, 'f'), (3, 'b'), (4, 'l')]
            while True:
                if path_queue.empty():
                    for move in test_moves:
                        path_queue.put(move)
                time.sleep(0.5)
        threading.Thread(target=auto_refill_path, args=(path_queue,), daemon=True).start()
        try:
            while True:
                user_msg = input("You: ")
                if user_msg.lower() in ['exit', 'quit']: break
                if user_msg: 
                    bridge.send(f'{user_msg}\n')
                    log.info(f"user input: {user_msg}")
                    print("You: ", end="", flush=True)      
        except (KeyboardInterrupt, EOFError):
            pass
        print("\nChat closed.")


    else:
        log.error("Invalid mode")
        sys.exit(1)




if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
