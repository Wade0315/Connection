from hm10_esp32 import HM10ESP32Bridge
import time
import sys
import threading
#from commucation import commucation
PORT = 'COM6'
EXPECTED_NAME = 'HM10_3'

data = open('data.txt', 'w')
#placement_buffer, movement_buffer = commucation()
movement_buffer = ['TURNRIGHT', 'TURNBACK', 'STOP']

def background_listener(bridge):
    

    while True:
        msg = bridge.listen()
        if msg == "Meet Node":
            bridge.send(f'{movement_buffer[curIndex % len(movement_buffer)]}\n')
            curIndex += 1
            print("You: ", end="", flush=True)
        elif msg:
            print(f"\r[HM10]: {msg}")
            print("You: ", end="", flush=True)
            data.write(f'{msg}\n')
        time.sleep(0.1)

def main():
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
    threading.Thread(target=background_listener, args=(bridge,), daemon=True).start()
    
    isSetup = False
    curIndex = 0

    try:
        while True:
            user_msg = input("You: ")
            if user_msg.lower() in ['exit', 'quit']: break
            if user_msg == "Setup" and isSetup == False:
                bridge.send(f'{movement_buffer[0]}\n{movement_buffer[1]}\n{movement_buffer[2]}\n')
                curIndex += 2
                isSetup = True
            if user_msg: bridge.send(user_msg)
    except (KeyboardInterrupt, EOFError):
        pass
    
    print("\nChat closed.")


if __name__ == "__main__":
    main()
data.close()