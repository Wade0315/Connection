import argparse
import logging
import os
import sys
import time

import numpy as np
import pandas
# from BTinterface import BTInterface
from log import setup_logging

from score import ScoreboardServer, ScoreboardFake
import threading
import queue
from genMovement import commute
from chat_hm10_esp32 import hm10_main
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
TEAM_NAME = "YOUR_TEAM_NAME"
SERVER_URL = "http://carcar.ntuee.org/scoreboard"
MAZE_FILE = "data/small_maze.csv"
BT_PORT = ""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="0: treasure-hunting, 1: self-testing", type=str)
    parser.add_argument("--maze-file", default=MAZE_FILE, help="Maze file", type=str)
    parser.add_argument("--startPoint", default=1, help="startPoint", type=int)
    parser.add_argument("--limit", default=1000, help="limit", type=int)
    parser.add_argument("--bt-port", default=BT_PORT, help="Bluetooth port", type=str)
    parser.add_argument(
        "--team-name", default=TEAM_NAME, help="Your team name", type=str
    )
    parser.add_argument("--server-url", default=SERVER_URL, help="Server URL", type=str)
    return parser.parse_args()



def main(mode: int, maze_file: str, startPoint: int, limit: int, bt_port: str, team_name: str, server_url: str):
    #maze = Maze(maze_file)
    #point = ScoreboardServer(team_name, server_url)
    #point = ScoreboardFake("your team name", "data/fakeUID.csv") # for local testing
    
    
    uid_queue = queue.Queue()
    path_queue = queue.Queue()

    ### Bluetooth connection haven't been implemented yet, we will update ASAP ###
    # interface = BTInterface(port=bt_port)
    # TODO : Initialize necessary variables

    if mode == "0":
        log.info("Mode 0: For treasure-hunting")
        # TODO : for treasure-hunting, which encourages you to hunt as many scores as possible
        scoreboard = ScoreboardServer("Team3", "http://140.112.175.18")
        time.sleep(1)
        threading.Thread(target=processor.score_processor, args=(uid_queue, scoreboard), daemon=True).start()
        hm10_main(uid_queue)

        for data_type, data in commute():
            if data_type == "GRAPH":
                log.debug(f'read graph!')
            elif data_type == "MOVE":
                log.debug(f'MOVEMENT: {data}')
            elif data_type == "NODE":
                log.debug(f'NODE: {data}')


        

        
    elif mode == "1":
        log.info("Mode 1: test read map.")
        threading.Thread(target=processor.gen_path_processor, args=(path_queue,maze_file,startPoint, limit), daemon=True).start()
        while True:
            try:
                path_json = path_queue.get(timeout=1) 
                log.info(f"get path: {path_json}")                
            except queue.Empty:
                pass
            except KeyboardInterrupt:
                log.info("end test")
                break
        # for data_type, data in commute():
        #     if data_type == "GRAPH":
        #         log.info(f'read graph!')
        #     elif data_type == "MOVE":
        #         log.info(f'MOVEMENT: {data}')
        #     elif data_type == "NODE":
        #         log.info(f'NODE: {data}')


    elif mode == "2": #crosstest
        log.info("Mode 1: cross test.")
        hm10_main(uid_queue)

        
    else:
        log.error("Invalid mode")
        sys.exit(1)




if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
