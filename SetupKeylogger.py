import os
from os import system
from os.path import exists
import json

# CONSTANTS
CONFIG_FILE = 'keylogger-config.json'
PYTHON_EXEC_PATH = 'python'  # used only when executable=False.
OPTIONS_CONFIG = {
    "auto-start": [False, True],
    "mode": ["local", "console", "debug"],
    "hide": [False, True],
    "exclude-typos": [True, False],
    "page-prefix": [""],
    "buffer-size": [20],
    "hotkeys": {
        "exit-hotkey": ["ctrl+alt+x"],
        "pause-hotkey": ["ctrl+alt+p"],
        "save-hotkey": ["ctrl+alt+s"]
    }
}

config = {}

def contains_all_options(fix, dict, options_dict):
    valid = True
    for k, v in options_dict.items():
        if not type(options_dict[k]) == type({}):
            if not k in dict:
                if fix: dict[k] = v[0]
                else: valid = False
            else:
                if len(v) > 1:
                    if not dict[k] in v:
                        if fix: dict[k] = v[0]
                        else: valid = False
                else:
                    if not type(dict[k]) == type(v[0]):
                        if fix: dict[k] = v[0]
                        else: valid = False
        else:
            if not k in dict: 
                dict[k] = {}
            valid = valid if contains_all_options(fix, dict[k], options_dict[k]) else False
    return valid

def contains_no_invalid_options(fix, dict, options_dict):
    valid = True
    invalid = []  
    for k, v in dict.items():
        if not k in options_dict:
            invalid.append(k)
            valid = False

    if fix: 
        for k in invalid:
            dict.pop(k)
        valid = True
    return valid


def is_valid_config(fix):
    global config
    valid = True
    valid = valid if contains_all_options(fix, config, OPTIONS_CONFIG) else False
    valid = valid if contains_no_invalid_options(fix, config, OPTIONS_CONFIG) else False
    
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
    is_valid_config(True)
    

# Menu for Configuration
def display_menu(title, menu):
    system('cls')  # clears stdout
    print(title)
    for k, menu in menu.items():
        print(k, menu)

def reset_config_default(conf):
    config[conf] = OPTIONS_CONFIG[conf][0]

def try_cast(value, type):
    if type == bool:
        if value in ['True', 'False']:
            return value == 'True'
        else:
            return value
    try:
        return type(value)
    except:
        return value

def get_values(dict, key_list):
    keys = key_list[:]
    for k, v in dict.items():
        if k == keys[0]:
            if type(v) == type({}):
                del keys[0]
                return get_values(v, keys)
            else:
                return v

def set_value(dict, key_list, value):
    keys = key_list[:]
    for k, v in dict.items():
        if k == keys[0]:
            if type(v) == type({}):
                del keys[0]
                set_value(v, keys, value)
            else:
                dict[k] = value
                break

def change_config_value(conf):
    
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

def change_config_menu(key_list):
    menu = {
        1: "Change",
        2: "Reset to Default",
        3: "Undo Change",
        4: "Save"
    }
    
    tmp = get_values(config, key_list)
    selection = 0
    while not selection == 4:
        val = get_values(config, key_list)
        name = key_list[-1]
        display_menu(name + " (" + str(val) + ")", menu)
        selection = int (
            input("Please enter your selection number: "))
            
        # Change Value
        if selection == 1:
            system('cls')  # clears stdout
            value = (input("Input value: "))
            value = try_cast(value, val.__class__)
            print(type(value))
            print(value)
            set_value(config, key_list, value)
            if not is_valid_config(False):
                set_value(config, key_list, tmp)
        # Reset to Default
        elif selection == 2:
            reset_config_default(key_list)
        # Undo Change
        elif selection == 3:
            set_value(config, key_list, tmp)
        # Save
        elif selection == 4:
            write_config()

# Menu for Configuration
def menu_options(key_list, menu):
    menu["Reset all to Default"] = 0
    menu["Exit"] = 0
    menu_items = dict(enumerate(menu, start=1))
    menu.pop("Reset all to Default")
    menu.pop("Exit")

    if key_list == "Keylogger Config":
        display_menu(key_list, menu_items)
    else:
        display_menu(key_list[-1], menu_items)

    selection = int(
        input("Please enter your selection number: "))
    
    if menu_items[selection] == "Reset all to Default":
        create_default_config()
        write_config()
    elif menu_items[selection] == "Exit":
        return False
    elif type(menu[menu_items[selection]]) == type({}):
        if key_list == "Keylogger Config":
            menu_options([menu_items[selection]], menu[menu_items[selection]])
        else:
            key_list.append(menu_items[selection])
            menu_options(key_list, menu[menu_items[selection]])
    else:    
        if key_list == "Keylogger Config":
            change_config_menu([menu_items[selection]])
        else:
            key_list.append(menu_items[selection])
            change_config_menu(key_list)
    return True

def main():
    if not read_config():
        create_default_config()
        write_config()
    else: 
        is_valid_config(True)

    global config

    running = True
    while running:
        running = menu_options("Keylogger Config", config)
    write_config()


if __name__ == "__main__":
    main()


# Code Resources: 
# Menu https://stackoverflow.com/questions/71943877/how-to-create-a-menu-system-for-a-console-terminal-application
# startup https://github.com/secureyourself7/python-keylogger