import argparse
import logging
import os
import sys
import time


import threading
import queue

from log import setup_logging
from hm10_esp32 import HM10ESP32Bridge
from score import ScoreboardServer, ScoreboardFake
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
MAZE_FILE = "data/medium_maze.csv"
STARTPOINT = 1
LIMIT = 1000
TEAM_NAME = "1_A_3"
SERVER_URL = "http://carcar.ntuee.org/scoreboard"
BT_PORT = "/dev/ttyUSB0"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="0: treasure-hunting, 1: self-testing", type=str)
    parser.add_argument("--maze-file", default=MAZE_FILE, help="Maze file", type=str)
    parser.add_argument("--startPoint", default=STARTPOINT, help="startPoint", type=int)
    parser.add_argument("--limit", default=LIMIT, help="limit", type=float)
    parser.add_argument("--bt-port", default=BT_PORT, help="Bluetooth port", type=str)
    parser.add_argument(
        "--team-name", default=TEAM_NAME, help="Your team name", type=str
    )
    parser.add_argument("--server-url", default=SERVER_URL, help="Server URL", type=str)
    return parser.parse_args()




def main(mode: int, maze_file: str, startPoint: int, limit: float, bt_port: str, team_name: str, server_url: str):
    #scoreboard = ScoreboardServer(team_name, server_url)
    #point = ScoreboardFake("your team name", "data/testUID.csv") # for local testing
    
    log.info("\n\n===================Start====================\n")
    
    status = {"current_node": startPoint, "step": 1, "time_left": limit}

    event_queue = queue.Queue() #store instant information
    path_queue = queue.Queue()  #store path 
    uid_queue = queue.Queue()   #eat uid

    restart_decision = threading.Event()  #eat the command if the car is gonna restart or continue
    ignore_event = threading.Event()

    if mode == "0":
        log.info("Mode 0: For treasure-hunting")
        scoreboard = ScoreboardServer("Team3", "http://140.112.175.18")
        bridge = HM10ESP32Bridge(port=bt_port)
        BT_setup.hm10_main(bridge, team_name)
        threading.Thread(target=BT_setup.background_listener, args=(bridge, event_queue, uid_queue, ignore_event), daemon=True).start()
        threading.Thread(target=processor.action_processor, args=(bridge, status, event_queue, path_queue, restart_decision, ignore_event), daemon=True).start()
        threading.Thread(target=processor.gen_path_processor, args=(path_queue,maze_file, status, restart_decision), daemon=True).start()
        threading.Thread(target=processor.score_processor, args=(uid_queue, scoreboard, status), daemon=True).start()

        try:
            while True:
                user_msg = input("You: ")
                if user_msg.lower() in ['exit', 'quit']: break
                if user_msg: 
                    if user_msg == "ready" or user_msg == "restart" or user_msg == "go":
                        event_queue.put(user_msg)
                        start_time = time.time()
                        threading.Thread(target=processor.current_status_handler, args=(status, startPoint, limit, start_time), daemon=True).start()
                    log.info(f"user input: {user_msg}")
        except KeyboardInterrupt:
            log.info("end test")
            pass
        print("\nChat closed.")

#======================================================================================================================================================
        
    elif mode == "1":
        log.info("Mode 1: test read map.")
        scoreboard = ScoreboardServer("Team3", "http://140.112.175.18")
        threading.Thread(target=processor.score_processor, args=(uid_queue, scoreboard, status), daemon=True).start()
        threading.Thread(target=processor.gen_path_processor, args=(path_queue,maze_file, status, restart_decision), daemon=True).start()
        start_time = time.time()
        threading.Thread(target=processor.current_status_handler, args=(status, startPoint, limit, start_time), daemon=True).start()

        try:
            time.sleep(1)
            while not path_queue.empty():
                log.info(path_queue.get())
            time.sleep(5)
            uid_queue.put("33333333")
            restart_decision.set()
            status['step'] = 7
            time.sleep(4)
            restart_decision.set()
            while not path_queue.empty():
                log.info(path_queue.get())
            time.sleep(5)
        except KeyboardInterrupt:
            log.info("end test")

#======================================================================================================================================================

    elif mode == "2": #crosstest
        log.info("Mode 2: cross test.")
        scoreboard = ScoreboardServer("Team3", "http://140.112.175.18")
        bridge = HM10ESP32Bridge(port=bt_port)
        BT_setup.hm10_main(bridge, team_name)
        threading.Thread(target=BT_setup.background_listener, args=(bridge, event_queue, uid_queue, ignore_event), daemon=True).start()
        threading.Thread(target=processor.action_processor, args=(bridge, status, event_queue, path_queue, restart_decision, ignore_event), daemon=True).start()

        def auto_refill_path(path_queue: queue.Queue):
            test_moves = [(0, 'r'), (1, 'b'), (2, 'f'), (3, 'b'), (4, 'l'), (5, 'b')]
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
                    if user_msg == "ready" or user_msg == "restart":
                        event_queue.put(user_msg)
                        start_time = time.time()
                        threading.Thread(target=processor.current_status_handler, args=(status, startPoint, limit, start_time), daemon=True).start()
                    log.info(f"user input: {user_msg}")
        except (KeyboardInterrupt, EOFError):
            pass
        print("\nChat closed.")

#======================================================================================================================================================

    elif mode == "3":   #scoreboard test
        log.info("Mode 3: scoreboard test.")
        scoreboard = ScoreboardServer("Team3", "http://140.112.175.18")
        threading.Thread(target=processor.score_processor, args=(uid_queue, scoreboard, status), daemon=True).start()
        uid_queue.put("33333333")
        uid_queue.put("00000000")
        uid_queue.put("11111111")
        uid_queue.put("9AC053BD")
        uid_queue.put("22222222")
        uid_queue.put("44444444")
        uid_queue.put("55555555")
        uid_queue.put("66666666")
        uid_queue.put("77777777")
        uid_queue.put("88888888")
        try:
            while True:
                user_msg = input("You: ")
                if user_msg.lower() in ['exit', 'quit']: break
        except (KeyboardInterrupt, EOFError):
            pass
        print("\nChat closed.")

    else:
        log.error("Invalid mode")
        sys.exit(1)




if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
