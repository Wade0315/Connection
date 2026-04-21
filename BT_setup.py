from hm10_esp32 import HM10ESP32Bridge
import time
import sys
import threading
import re
import queue
import logging


log = logging.getLogger(__name__)

def background_listener(bridge: HM10ESP32Bridge, event_queue: queue.Queue, uid_queue: queue.Queue, ignore_event: threading.Event):
    while True:
        with open("data.txt", "a") as data:
            msg = bridge.listen()

            if ignore_event.is_set():
                log.debug(f"remove trash report")
                continue

            if msg:
                log.info(f"\r[HM10]: {msg}")
                data.write(f"{msg}\n")
            if "NN" in msg:
                event_queue.put("NN")
                log.info(f"put {"NN"} to event_queue")
            elif "Please input ready" in msg:
                print("Please input ready", flush=True)
                print("You: ", end = '', flush=True) 
                
            match = re.search(r"([0-9A-Fa-f]{8})", msg)   # eat "{UID}"
            if match:
                uid_value = match.group(1)
                uid_queue.put(uid_value)
                log.info(f'get uid: {uid_value}')
                event_queue.put("reach")
            time.sleep(0.08)

def hm10_main(bridge: HM10ESP32Bridge, team_name: str):

    # 1. Configuration Check
    current_name = bridge.get_hm10_name()
    if current_name != team_name:
        log.info(f"Target mismatch. Current: {current_name}, Expected: {team_name}")
        log.info(f"Updating target name to {team_name}...")
        
        if bridge.set_hm10_name(team_name):
            log.info("✅ Name updated successfully. Resetting ESP32...")
            bridge.reset()
            # Re-init after reset
            #bridge = HM10ESP32Bridge(port=PORT)
        else:
            log.info("❌ Failed to set name. Exiting.")
            sys.exit(1)

    # 2. Connection Check
    status = bridge.get_status()
    if status != "CONNECTED":
        log.info(f"⚠️ ESP32 is {status}. Please ensure HM-10 is advertising. Exiting.")
        sys.exit(0)

    log.info(f"✨ Ready! Connected to {team_name}")



