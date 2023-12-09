import keyboard
from keyboard import KeyboardEvent
import win32api
import win32event
import win32console
import win32gui
import winerror
import json
import os
from os.path import exists, join
import sys
from datetime import date
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
# Time when the last save of the heatmap was
last_save = 0

# Read config from json file
def read_config():
    config_path = join(DIR_PATH, CONFIG_FILE)
    # Check file exist and is not empty
    if exists(config_path) and not os.stat(config_path).st_size == 0:
        # Open file and read config 
        with open(config_path, "r") as read_file:
            global config
            config = json.load(read_file)
            return True
    else:
        return False

# Read the configurarion
if read_config():
    if not config["hide"]:
        print("Successfully load configuration.")
else:
    print("Failed load configuration.")
    exit()

# Disallowing multiple instances with same prefix
mutex = win32event.CreateMutex(None, 1, 'mutex_var_Start' + config["file-prefix"])
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
    reg_value = 'CMD /k "cd ' + DIR_PATH + ' && ' + 'py' + ' ' + '"' + CURRENT_FILE_PATH + '"'

    try:
        SetValueEx(key2change, LOGGER_NAME, 0, REG_SZ, reg_value)
        if not config["hide"]:
            print("Keylogger applied to startup.")
    except Exception as e:
        if not config["hide"]:
            print("Error occurred while applying keylogger to startup:")
            print(e)

# Remove from startup 
def remove_from_startup():
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'
    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)

    try:
        DeleteValue(key2change, LOGGER_NAME)  
        if not config["hide"]:
            print("Keylogger removed from startup.")
    except Exception as e:
        if not config["hide"]:
            print("No keylogger is applied to startup.")

# Debug logger
def log_debug():
    global config, heatmap_buffer
    if len(heatmap_order) > 0:
            # Print the last pressed key to console
            if len(heatmap_order[-1]["key"]) == 1:
                print(heatmap_buffer[heatmap_order[-1]["key"][0]])
                return True
            # Print the last pressed keycombinaiton to console
            elif len(heatmap_order[-1]["key"]) == 2:
                print(heatmap_buffer[heatmap_order[-1]["key"][0] + heatmap_order[-1]["key"][1]])
                return True
    return False

# Append file with pressed keys
def log_local():
    global config, heatmap_buffer 
    # Remove elements with mentions = 0     
    unused = []
    for k,v in heatmap_buffer.items():
        if v["mentions"] == 0:
            unused.append(k)
    for k in unused:
        del heatmap_buffer[k]
    # Sort elements by mentions
    sorted_buffer = sorted(heatmap_buffer.items(), key=lambda x:x[1]["mentions"], reverse=True)
    heatmap_buffer = dict(sorted_buffer)
    # Save in file
    path = join(DIR_PATH, os.pardir, BOOK_PATH)
    if not exists(path):
        os.makedirs(path) 
    file = join(path, (("" if config["file-prefix"] == "" else config["file-prefix"] + "_") + "heatmap_" + date.today().strftime('%Y-%m-%d') + ".json"))
    with open(file, "w") as write_file:
        json.dump(heatmap_buffer, write_file, indent=4)
    return True

# Log with configured output
def log_it():
    global config, last_save
    if config["output"] == "local":   
        if round(time.time_ns() / 1000000) - last_save > config["save-intervall"]:
            last_save = round(time.time_ns() / 1000000)
            return log_local()
    elif config["output"] == "debug":
        return log_debug()
    return False
    
def key_callback(event: KeyboardEvent):
    global heatmap_buffer, heatmap_order, paused

    # while paused no logging
    if paused:
        return False
    
    # event key up 
    if event.event_type == 'up':
        return False
    
    # Current time when key is pressed
    now_ms = round(event.time * 1000)

    # Remove pressed keys there are to old to delete
    if not config["typos"]["processing-time"] == -1:
        to_old = []
        for e in heatmap_order:
            if now_ms - e["time"] > config["typos"]["processing-time"]:
                to_old.append(e)
        for k in to_old:
            heatmap_order.remove(k)
    
    # Console output
    if config["output"] == 'console':
        print("event:",{
            "name": event.name,
            "event_type": event.event_type,
            "scan_code": event.scan_code,
            "time": event.time,
            "device": event.device,
            "is_keypad": event.is_keypad,
            "modifiers": event.modifiers
        })
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
        if config["typos"]["exclude-typos"]:
            if len(heatmap_order) > 0:
                if len(heatmap_order[-1]["key"]) == 1:
                    heatmap_buffer[heatmap_order[-1]["key"][0]]["mentions"] = heatmap_buffer[heatmap_order[-1]["key"][0]]["mentions"] - 1
                elif len(heatmap_order[-1]["key"]) == 2:
                    heatmap_buffer[heatmap_order[-1]["key"][-1]]["mentions"] = heatmap_buffer[heatmap_order[-1]["key"][-1]]["mentions"] - 1
                    heatmap_buffer[(heatmap_order[-1]["key"][0] + heatmap_order[-1]["key"][1])]["mentions"] = heatmap_buffer[(heatmap_order[-1]["key"][0] + heatmap_order[-1]["key"][1])]["mentions"] - 1
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
    path = join(DIR_PATH, os.pardir, BOOK_PATH)
    file = join(path, (("" if config["file-prefix"] == "" else config["file-prefix"] + "_") + "heatmap_" + date.today().strftime('%Y-%m-%d') + ".json"))
    if exists(file) and not os.stat(file).st_size == 0:
        with open(file, "r") as read_file:
            global heatmap_buffer
            heatmap_buffer = json.load(read_file)
            return True
    return False    

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
    if config["output"] == "local":
        if not log_local() and not config["hide"]:
            print("Something went wrong while saving!")
    if not config["hide"]:
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
    if read_heatmap():
        print("Loaded existing heatmap.")
    else:
        print("No Heatmap for today exist. Will be created.")

    # Setup save time
    last_save = round(time.time_ns() / 1000000)

    main()
