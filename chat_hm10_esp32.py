from hm10_esp32 import HM10ESP32Bridge
import time
import sys
import threading
import re
import queue
import logging

from processor import action_processor

log = logging.getLogger(__name__)

#from commucation import commucation
PORT = 'COM6'
EXPECTED_NAME = 'HM10_3'


def background_listener(bridge: HM10ESP32Bridge, uid_queue: queue.Queue, event_queue: queue.Queue):
    while True:
        msg = bridge.listen()
        if msg == "NODELEAVE":
            event_queue.put(f'{msg}\n')
        match = re.match(r"^\s*UID\s*:\s*([0-9A-Fa-f]{8})$", msg)   # eat "UID: {UID}"
        if match:
            uid_value = match.group(1)
            uid_queue.put(uid_value)
        if msg:
            print(f"\r[HM10]: {msg}")
            print("You: ", end="", flush=True)
        time.sleep(0.02)

def hm10_main(uid_queue:queue.Queue, event_queue: queue.Queue, decision_queue: queue.Queue):
    bridge = HM10ESP32Bridge(port=PORT)

    # 1. Configuration Check
    current_name = bridge.get_hm10_name()
    if current_name != EXPECTED_NAME:
        print(f"Target mismatch. Current: {current_name}, Expected: {EXPECTED_NAME}")
        print(f"Updating target name to {EXPECTED_NAME}...")
        
        if bridge.set_hm10_name(EXPECTED_NAME):
            print("✅ Name updated successfully. Resetting ESP32...")
            bridge.reset()
            # Re-init after reset
            #bridge = HM10ESP32Bridge(port=PORT)
        else:
            print("❌ Failed to set name. Exiting.")
            sys.exit(1)

    # 2. Connection Check
    status = bridge.get_status()
    if status != "CONNECTED":
        print(f"⚠️ ESP32 is {status}. Please ensure HM-10 is advertising. Exiting.")
        sys.exit(0)

    print(f"✨ Ready! Connected to {EXPECTED_NAME}")
    threading.Thread(target=background_listener, args=(bridge,uid_queue, event_queue), daemon=True).start()
    threading.Thread(target=action_processor, args=(bridge, event_queue, decision_queue), daemon=True).start()
    #isSetup = False

    try:
        while True:
            user_msg = input("You: ")
            if user_msg.lower() in ['exit', 'quit']: break
            if user_msg: bridge.send(f'{user_msg}\n')
            if user_msg == "ready":
                event_queue.put(f"{user_msg}")
                print("You: ", end="", flush=True)
            
    except (KeyboardInterrupt, EOFError):
        pass
    
    print("\nChat closed.")




if __name__ == "__main__":
    uid_queue = queue.Queue()
    uid_queue.put("10BA617E")
    uid_queue.put("84EAB017")
    uid_queue.put("50335F7E")
    hm10_main(uid_queue)
