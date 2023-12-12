import os
from os import system
from os.path import join
import sys
from KeyloggerConfig import KeyloggerConfig

# Config File
CONFIG_FILE = 'keylogger.config.json'
# Directory path
DIR_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))
# Config object
config = {}

# Menu for Configuration12
def display_menu(title, menu: list):
    system('cls')  # clears stdout
    print(title)
    for i in range(len(menu)):
        print(i, menu[i]["label"])

def change_config_menu(option):
    menu = [
        {"label": "change"},
        {"label": "undo change"},
        {"label": "reset to default"},
        {"label": "exit"}
    ]
    
    tmp = option["get"]()
    selection = 0
    while not selection == 3:
        val = option["get"]()
        name = option["label"]
        display_menu(name + " (" + str(val) + ")", menu)
        selection = int (
            input("Please enter your selection number: "))
            
        # Change Value
        if selection == 0:
            system('cls')  # clears stdout
            value = (input("Input value: "))
            option["set"](value)
        # Reset to Default
        elif selection == 1:
            option["default"]()
        # Undo Change
        elif selection == 2:
            option["set"](tmp)

# Menu for Configuration
def menu_options(menu):
    menu.append({
        "label": "save and exit"
    })

    display_menu("Keylogger Config", menu)

    selection = int(
        input("Please enter your selection number: "))

    if menu[selection]["label"] == "save and exit":
        return False
    else:    
        change_config_menu(menu[selection])
    return True

def main():
    global config
    config = KeyloggerConfig()
    config.read_config(join(DIR_PATH, CONFIG_FILE))  

    running = True
    while running:
        running = menu_options(config.get_options())
    config.write_config(join(DIR_PATH, CONFIG_FILE))

if __name__ == "__main__":
    main()


# Code Resources: 
# Menu https://stackoverflow.com/questions/71943877/how-to-create-a-menu-system-for-a-console-terminal-application
# startup https://github.com/secureyourself7/python-keylogger