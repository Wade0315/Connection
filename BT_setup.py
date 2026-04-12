from hm10_esp32 import HM10ESP32Bridge
import time
import sys
import threading
import re
import queue
import logging

import main

log = logging.getLogger(__name__)


def background_listener(bridge: HM10ESP32Bridge, uid_queue: queue.Queue, event_queue: queue.Queue):
    while True:
        msg = bridge.listen()
        if msg == "NODELEAVE":
            event_queue.put(msg)
        match = re.match(r"^\s*UID\s*:\s*([0-9A-Fa-f]{8})$", msg)   # eat "UID: {UID}"
        if match:
            uid_value = match.group(1)
            uid_queue.put(uid_value)
        if msg:
            log.info(f"\r[HM10]: {msg}")
        time.sleep(0.08)

def hm10_main(bridge: HM10ESP32Bridge):

    # 1. Configuration Check
    current_name = bridge.get_hm10_name()
    if current_name != main.TEAM_NAME:
        log.info(f"Target mismatch. Current: {current_name}, Expected: {main.TEAM_NAME}")
        log.info(f"Updating target name to {main.TEAM_NAME}...")
        
        if bridge.set_hm10_name(main.TEAM_NAME):
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

    log.info(f"✨ Ready! Connected to {main.TEAM_NAME}")





