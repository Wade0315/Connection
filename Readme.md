settings:
1. connect Vscode in Ubuntu
2. setup venv env
3. pip install pyserial numpy requests python-socketio
4. in extension install serial monitor(from microsoft)
5. use Ctrl + shift + P, click "View: Toggle Serial Monitor"

(ALternating method) :
1. (in windows) winget install --interactive --exact dorssel.usbipd-win
2. (in wsl) sudo apt install linux-tools-virtual hwdata
3. (in wsl) sudo apt install usbutils
4. (in wsl) sudo update-alternatives --install /usr/local/bin/usbip usbip 
    `ls /usr/lib/linux-tools/*usbip tail -n1` 20
5. reopen your computor
6. (in windows powershell administor mode) usbipd list 
7. remember your BUSID
8. (in windows powershell administor mode) usbipd bind --busid {BUSID}
9. (in windows powershell administor mode) usbipd attach --wsl --busid {BUSID}
10. (in linux) lsusb
11. ls /dev/ttyUSB*
12. sudo chmod 666 /dev/ttyUSB0


How to execute:
1. connect to venv
2. python3 main.py 1 <optional --maze-file maze.csv ...>
3. open a new terminal, use tail -f system.log to see log