import keyboard
import win32api
import win32event
import win32console
import win32gui
import winerror
import json
import os
from os.path import exists, join
import sys
import time
from winreg import SetValueEx, OpenKey, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ, DeleteValue

# Folder where the pages of your book get logged
BOOK_PATH = 'myBook'
# Config File
CONFIG_FILE = 'keylogger-config.json'
# Name of The Logger (Be carefull changeing this may results in unremoveable registered autostart)
LOGGER_NAME = "Harmless Keylogger"
# File path
CURRENT_FILE_PATH = os.path.realpath(sys.argv[0])
# Directory path
DIR_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

# Config Dict
config = {}
# Buffer for Heatmap
heatmap_buffer = {}
heatmap_order = []
# Paused logging
paused = False

# Read confgi from json file
def read_config():
    config_path = join(DIR_PATH, CONFIG_FILE)
    if exists(config_path) and not os.stat(config_path).st_size == 0:
        with open(config_path, "r") as read_file:
            global config
            config = json.load(read_file)
            return True
    else:
        return False

# Read the configurarion
read_config()

# Disallowing multiple instances
mutex = win32event.CreateMutex(None, 1, 'mutex_var_Start' + ('' if not config["output"] == 'debug' else '_debug'))
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    if not config["hide"] or (config["output"] == 'debug'):
        print("Multiple instances are not allowed")
    exit(0)

# Add to startup for persistence
def add_to_startup():
    global config
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)

    reg_value_prefix = 'CMD /k "cd ' + DIR_PATH + ' && ' + 'py' + ' '
    reg_value_postfix = '"'

    reg_value = reg_value_prefix + '"' + CURRENT_FILE_PATH + reg_value_postfix

    try:
        SetValueEx(key2change, LOGGER_NAME, 0, REG_SZ, reg_value)
    except Exception as e:
        if config["output"] == 'debug':
            print(e)

# Remove from startup f
def remove_from_startup():
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)

    try:
        DeleteValue(key2change, LOGGER_NAME)  
    except Exception as e:
        if config["output"] == 'debug':
            print(e, ". Not critical if logger isn't applied to startup")

# Debug logger
def log_debug():
    global config, heatmap_buffer
    if len(heatmap_order) > 0:
            if len(heatmap_order[-1]["key"]) == 1:
                print(heatmap_buffer[heatmap_order[-1]["key"][0]])
            if len(heatmap_order[-1]["key"]) == 2:
                print(heatmap_buffer[heatmap_order[-1]["key"][0] + heatmap_order[-1]["key"][1]])
    return True

# Append file with pressed keys
def log_local():
    global config, heatmap_buffer
    path = join(DIR_PATH, BOOK_PATH)
    if not exists(path):
            os.makedirs(path)       
    unused = []
    for k,v in heatmap_buffer.items():
        if v["mentions"] == 0:
            unused.append(k)
    for k in unused:
        del heatmap_buffer[k]
    file = join(path, (("" if config["file-prefix"] == "" else config["file-prefix"] + "_") + "heatmap.json"))
    with open(file, "w") as write_file:
        json.dump(heatmap_buffer, write_file, indent=4)
    return True

# Log with configured output
def log_it():
    global config
    if config["output"] == "local":        
        log_local()
    elif config["output"] == "debug":
        log_debug()
    return True
    
def key_callback(event):
    global heatmap_buffer, heatmap_order, paused

    now_ms = round(time.time_ns() / 1000000)

    # while paused no logging
    if paused:
        return False
    
    # event key up 
    if event.event_type == 'up':
        return False
    
    # Console output
    if config["output"] == 'console':
        print(event.name, event.scan_code)
        return True
    
    key_pressed = {}
    # Key Represention
    # Shift
    if event.scan_code == 42 or event.scan_code == 54:
        return False
    # Space
    elif event.name == 'space':
        key_pressed = {
            "name": event.name,
            "scancode": event.scan_code,
            "value": " ",
            "length": 1
        }
    # Enter
    elif event.name == 'enter':
        key_pressed = {
            "name": event.name,
            "scancode": event.scan_code,
            "value": "\n",
            "length": 1
        }
    # Backspace
    elif event.name == 'backspace':
        if config["exclude-typos"]:
            if len(heatmap_order) > 0:
                if len(heatmap_order[-1]["key"]) == 1:
                    heatmap_buffer[heatmap_order[-1]["key"][0]]["mentions"] = heatmap_buffer[heatmap_order[-1]["key"][0]]["mentions"] - 1
                    # heatmap_order.pop()
                elif len(heatmap_order[-1]["key"]) == 2:
                    heatmap_buffer[heatmap_order[-1]["key"][-1]]["mentions"] = heatmap_buffer[heatmap_order[-1]["key"][-1]]["mentions"] - 1
                    heatmap_buffer[(heatmap_order[-1]["key"][0] + heatmap_order[-1]["key"][1])]["mentions"] = heatmap_buffer[(heatmap_order[-1]["key"][0] + heatmap_order[-1]["key"][1])]["mentions"] - 1
                    # heatmap_order[-1]["key"] = [heatmap_order[-1]["key"][0]]
                heatmap_order.pop()
                
    # Letters
    elif len(event.name) == 1:
        key_pressed = {
        "name": event.name,
        "scancode": event.scan_code,
        "value": event.name,
        "length": 1
        }
    # Other
    else:
        print("Not saved key: ")
        print(event.name, event.scan_code)
    
    if not key_pressed == {}:
        index = [key_pressed["name"]]
        # Add combination key to heatmap
        if len(heatmap_order) > 0 and now_ms - heatmap_order[-1]["time"] < config["combination-time"]:
            if len(heatmap_order[-1]["key"]) == 1:
                temp = {}
                temp["name"] = [heatmap_buffer[heatmap_order[-1]["key"][0]]["name"], key_pressed["name"]]
                temp["scancode"] = [heatmap_buffer[heatmap_order[-1]["key"][0]]["scancode"], key_pressed["scancode"]]
                temp["value"] = [heatmap_buffer[heatmap_order[-1]["key"][0]]["value"], key_pressed["value"]]
                temp["length"] = 2
                index = [temp["name"][0], temp["name"][1]]
            elif len(heatmap_order[-1]["key"]) == 2:
                temp = {}
                temp["name"] = [heatmap_buffer[heatmap_order[-1]["key"][-1]]["name"], key_pressed["name"]]
                temp["scancode"] = [heatmap_buffer[heatmap_order[-1]["key"][-1]]["scancode"], key_pressed["scancode"]]
                temp["value"] = [heatmap_buffer[heatmap_order[-1]["key"][-1]]["value"], key_pressed["value"]]
                temp["length"] = 2
                index = [temp["name"][0], temp["name"][1]]
            if (temp["name"][0] + temp["name"][1]) in heatmap_buffer and "mentions" in heatmap_buffer[(temp["name"][0] + temp["name"][1])]:
                heatmap_buffer[(temp["name"][0] + temp["name"][1])]["mentions"] = heatmap_buffer[(temp["name"][0] + temp["name"][1])]["mentions"] + 1
            else:
                temp["mentions"] = 1
                heatmap_buffer[(temp["name"][0] + temp["name"][1])] = temp
        # Add single key to heatmap
        if key_pressed["name"] in heatmap_buffer and "mentions" in heatmap_buffer[key_pressed["name"]]:
            heatmap_buffer[key_pressed["name"]]["mentions"] = heatmap_buffer[key_pressed["name"]]["mentions"] + 1
        else:
            key_pressed["mentions"] = 1
            heatmap_buffer[key_pressed["name"]] = key_pressed

        heatmap_order.append({
            "key": index,
            "time": now_ms
        })
    
    return log_it()

def pause_logging():
    global paused
    if not config["hide"] or (config["output"] == 'debug'):
        print(LOGGER_NAME + (" paused" if not paused else " continue"))
    paused = not paused

def read_heatmap():
    path = join(DIR_PATH, BOOK_PATH)
    file = join(path, (("" if config["file-prefix"] == "" else config["file-prefix"] + "_") + "heatmap.json"))
    if exists(file) and not os.stat(file).st_size == 0:
        with open(file, "r") as read_file:
            global heatmap_buffer
            heatmap_buffer = json.load(read_file)

def hide():
    if not config["output"] == 'debug':
        # Hide Console
        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, 0)
        return True
    else:
        print("Console Hide")

def main():
    if not config["hide"] or (config["output"] == 'debug'):
        print(LOGGER_NAME + " started")
    keyboard.hook(key_callback)
    # To Pause the Keylogger (ctrl + alt + p)
    keyboard.add_hotkey(config["hotkeys"]["pause-hotkey"], pause_logging)
    # To save the buffer (ctrl + alt + s)
    keyboard.add_hotkey(config["hotkeys"]["save-hotkey"], log_local)
    # To Exit the Keylogger with safing the buffer (ctrl + alt + e)
    keyboard.wait(config["hotkeys"]["exit-hotkey"]) 
    log_it()
    if not config["hide"] or (config["output"] == 'debug'):
        print(LOGGER_NAME + " stopped.")
    exit()

if __name__ == '__main__':
    # Hide comand prompt
    if config["hide"]:
        hide()

    # Add to startup
    if config["auto-start"]:
        add_to_startup()
    else: 
        remove_from_startup()

    # Read already saved values 
    read_heatmap()

    main()
