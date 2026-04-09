import argparse
import logging
import os
import sys
import time

import numpy as np
import pandas
# from BTinterface import BTInterface


from score import ScoreboardServer, ScoreboardFake
import threading
import queue
from genMovement import commute
from chat_hm10_esp32 import hm10_main

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

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
    parser.add_argument("--bt-port", default=BT_PORT, help="Bluetooth port", type=str)
    parser.add_argument(
        "--team-name", default=TEAM_NAME, help="Your team name", type=str
    )
    parser.add_argument("--server-url", default=SERVER_URL, help="Server URL", type=str)
    return parser.parse_args()



def main(mode: int, bt_port: str, team_name: str, server_url: str, maze_file: str):
    #maze = Maze(maze_file)
    #point = ScoreboardServer(team_name, server_url)
    
    point = ScoreboardFake("your team name", "data/fakeUID.csv") # for local testing

    ### Bluetooth connection haven't been implemented yet, we will update ASAP ###
    # interface = BTInterface(port=bt_port)
    # TODO : Initialize necessary variables

    if mode == "0":
        log.info("Mode 0: For treasure-hunting")
        # TODO : for treasure-hunting, which encourages you to hunt as many scores as possible
        uid_queue = queue.Queue()
        scoreboard = ScoreboardServer("Monday_aferernoon_Team3", "http://140.112.175.18")
        time.sleep(1)
        threading.Thread(target=score_processor, args=(uid_queue, scoreboard), daemon=True).start()
        hm10_main(uid_queue)

        for data_type, data in commute():
            if data_type == "GRAPH":
                print(f'read graph!')
            elif data_type == "MOVE":
                print(f'MOVEMENT: {data}')
            elif data_type == "NODE":
                print(f'NODE: {data}')
        

        

        
    elif mode == "1":
        log.info("Mode 1: Self-testing mode.")
        # TODO: You can write your code to test specific function.
        for data_type, data in commute():
            if data_type == "GRAPH":
                print(f'read graph!')
            elif data_type == "MOVE":
                print(f'MOVEMENT: {data}')
            elif data_type == "NODE":
                print(f'NODE: {data}')

    else:
        log.error("Invalid mode")
        sys.exit(1)

def score_processor(uid_queue: queue.Queue, scoreboard: ScoreboardServer):
    print("waiting for UID...")
    while True:
        uid = uid_queue.get() 
        log.debug(f"Get uid: {uid}")
        
        score, time_remaining = scoreboard.add_UID(uid)
        current_score = scoreboard.get_current_score()
        
        log.info(f"Current score: {current_score}")
        print("You: ", end="", flush=True)


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
