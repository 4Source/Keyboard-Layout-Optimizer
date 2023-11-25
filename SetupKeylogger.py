import os
from os import system
from os.path import exists
import sys
import json
from winreg import SetValueEx, OpenKey, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ, DeleteValue

# CONSTANTS
CONFIG_FILE = 'keylogger-config.json'
PYTHON_EXEC_PATH = 'python'  # used only when executable=False.
OPTIONS_CONFIG = {
    "auto-start": [False, True],
    "mode": ["local", "debug"]
}

config = {}

def is_valid_config(fix):
    global config
    valid = True
    for k, v in OPTIONS_CONFIG.items():
        if not k in config:
            if fix: config[k] = v[0]
            else: valid = False
        else:
            if not config[k] in v:
                if fix: config[k] = v[0]
                else: valid = False

    invalid = []  
    for k, v in config.items():
        if not k in OPTIONS_CONFIG:
            invalid.append(k)
            valid = False

    if fix: 
        for k in invalid:
            config.pop(k)
        valid = True
    
    return valid

def read_config():
    if exists(CONFIG_FILE) and not os.stat(CONFIG_FILE).st_size == 0:
        with open(CONFIG_FILE, "r") as read_file:
            global config
            config = json.load(read_file)
            if not is_valid_config(True): 
                write_config()
            return True
    else:
        return False

def write_config():
    with open(CONFIG_FILE, "w") as write_file:
        global config
        is_valid_config(True)
        json.dump(config, write_file, indent=4)

def create_default_config():
    global config
    for k, v in OPTIONS_CONFIG.items():
        config[k] = v[0]

# Menu for Configuration
def display_menu(title, menu):
    system('cls')  # clears stdout
    print(title)
    for k, menu in menu.items():
        print(k, menu)

def change_config_value(conf):
    system('cls')  # clears stdout
    print(conf + " (" + str(config[conf]) + ")")
    value = input("Input value: ")
    if type(OPTIONS_CONFIG[conf][0]) == bool:
        if value == "False":
            value = False
        elif value == "True":
            value = True
        config[conf] = value
    elif type(OPTIONS_CONFIG[conf][0]) == int:
        config[conf] = int(value)
    else:
        config[conf] = value

def reset_config_default(conf):
    config[conf] = OPTIONS_CONFIG[conf][0]
    
def change_config_menu(conf):
    if conf == "Reset all to Default":
        create_default_config()
        write_config()
    elif conf == "Exit":
        write_config()
        exit()
    else:
        menu = {
            1: "Change",
            2: "Reset to Default",
            3: "Undo Change",
            4: "Save"
        }
        tmp = config[conf]
        selection = 0
        while not selection == 4:
            display_menu(conf + " (" + str(config[conf]) + ")", menu)
            selection = int (
                input("Please enter your selection number: "))
                
            # Change Value
            if selection == 1:
                change_config_value(conf)
                if not is_valid_config(False):
                    system('cls')  # clears stdout
                    print("Input is not a valid input. Try: ")
                    for o in OPTIONS_CONFIG[conf]:
                        print(o)
                    input("Press Any Key to continue")
                    config[conf] = tmp
            # Reset to Default
            elif selection == 2:
                reset_config_default(conf)
            # Undo Change
            elif selection == 3:
                config[conf] = tmp
            # Save
            elif selection == 4:
                write_config()

def main():
    if not read_config():
        create_default_config()
        write_config()

    global config

    # Create a menu dictionary where the key is an integer number and the
    # value is a function name.
    config["Reset all to Default"] = 0
    config["Exit"] = 0
    menu_title = "Keylogger Config"
    menu_items = dict(enumerate(config, start=1))
    config.pop("Reset all to Default")
    config.pop("Exit")

    while True:
        display_menu(menu_title, menu_items)
        selection = int(
            input("Please enter your selection number: "))
        change_config_menu(menu_items[selection]) 


if __name__ == "__main__":
    main()


# Code Resources: 
# Menu https://stackoverflow.com/questions/71943877/how-to-create-a-menu-system-for-a-console-terminal-application
# startup https://github.com/secureyourself7/python-keylogger