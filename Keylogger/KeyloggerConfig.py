import os
import json
from os.path import exists, join
from enum import Enum
import sys

# Config File
CONFIG_FILE = 'keylogger-config.json'
# Directory path
DIR_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

class KeyloggerConfig:
    _auto_start: bool
    _output: str
    _hide: str
    _exclude_typos: bool
    _processing_time: int
    _file_prefix: str
    _combination_time: int
    _save_interval: int
    _exit_hotkey: str
    _pause_hotkey: str
    _save_hotkey: str
    _visible_hotkey: str

    def __init__(self):
        self.set_default_auto_start()
        self.set_default_output()
        self.set_default_hide()
        self.set_default_exclude_typos()
        self.set_default_processing_time()
        self.set_default_file_prefix()
        self.set_default_combination_time()
        self.set_default_save_interval()
        self.set_default_exit_hotkey()
        self.set_default_pause_hotkey()
        self.set_default_save_hotkey()
        self.set_default_visible_hotkey()

    
    # Read config from json file
    def read_config(self, config_file_path): 
        config_json = {}
        # Check file exist and is not empty
        if exists(config_file_path) and not os.stat(config_file_path).st_size == 0:
            # Open file and read config 
            with open(config_file_path, "r") as read_file:
                config_json = json.load(read_file)
        if config_json:
            if "auto-start" in config_json:
                self.set_auto_start(config_json["auto-start"])
            if "output" in config_json:
                self.set_output(config_json["output"])
            if "hide" in config_json:
                self.set_hide(config_json["hide"])
            if "typos" in config_json:
                if "exclude-typos" in config_json["typos"]:
                    self.set_exclude_typos(config_json["typos"]["exclude-typos"])
                if "exclude-typos" in config_json["typos"]:
                    self.set_processing_time(config_json["typos"]["processing-time"])
            if "file-prefix" in config_json:
                self.set_file_prefix(config_json["file-prefix"])
            if "combination-time" in config_json:
                self.set_combination_time(config_json["combination-time"])
            if "save-interval" in config_json:
                self.set_save_interval(config_json["save-interval"])
            if "hotkeys" in config_json:
                if "exit-hotkey" in config_json["hotkeys"]:
                    self.set_exit_hotkey(config_json["hotkeys"]["exit-hotkey"])
                if "pause-hotkey" in config_json["hotkeys"]:
                    self.set_pause_hotkey(config_json["hotkeys"]["pause-hotkey"])
                if "save-hotkey" in config_json["hotkeys"]:
                    self.set_save_hotkey(config_json["hotkeys"]["save-hotkey"])
                if "visible-hotkey" in config_json["hotkeys"]:
                    self.set_visible_hotkey(config_json["hotkeys"]["visible-hotkey"])
            
    # Write config to json file
    def write_config(self, config_file):
        config_json = {}
        config_json["auto-start"] = self.get_auto_start()
        config_json["output"] = self.get_output()
        config_json["hide"] = self.get_hide()
        config_json["typos"] = {}
        config_json["typos"]["exclude-typos"] = self.get_exclude_typos()
        config_json["typos"]["processing-time"] = self.get_processing_time()
        config_json["file-prefix"] = self.get_file_prefix()
        config_json["combination-time"] = self.get_combination_time()
        config_json["save-interval"] = self.get_save_interval()
        config_json["hotkeys"] = {}
        config_json["hotkeys"]["exit-hotkey"] = self.get_exit_hotkey()
        config_json["hotkeys"]["pause-hotkey"] = self.get_pause_hotkey()
        config_json["hotkeys"]["save-hotkey"] = self.get_save_hotkey()
        config_json["hotkeys"]["visible-hotkey"] = self.get_visible_hotkey()
        with open(config_file, "w") as write_file:
            json.dump(config_json, write_file, indent=4)

    def get_options(self):
        options = []
        options.append({
            "label": "auto-start",
            "description": "", 
            "get": self.get_auto_start,
            "set": self.set_auto_start,
            "default": self.set_default_auto_start
        })
        options.append({
            "label": "output",
            "description": "", 
            "get": self.get_output,
            "set": self.set_output,
            "default": self.set_default_output
        })
        options.append({
            "label": "hide",
            "description": "", 
            "get": self.get_hide,
            "set": self.set_hide,
            "default": self.set_default_hide
        })
        options.append({
            "label": "exclude-typos",
            "description": "", 
            "get": self.get_exclude_typos,
            "set": self.set_exclude_typos,
            "default": self.set_default_exclude_typos
        })
        options.append({
            "label": "processing-time",
            "description": "", 
            "get": self.get_processing_time,
            "set": self.set_processing_time,
            "default": self.set_default_processing_time
        })
        options.append({
            "label": "file-prefix",
            "description": "", 
            "get": self.get_file_prefix,
            "set": self.set_file_prefix,
            "default": self.set_default_file_prefix
        })
        options.append({
            "label": "combination-time",
            "description": "", 
            "get": self.get_combination_time,
            "set": self.set_combination_time,
            "default": self.set_default_combination_time
        })
        options.append({
            "label": "save-interval",
            "description": "", 
            "get": self.get_save_interval,
            "set": self.set_save_interval,
            "default": self.set_default_save_interval
        })
        options.append({
            "label": "exit-hotkey",
            "description": "", 
            "get": self.get_exit_hotkey,
            "set": self.set_exit_hotkey,
            "default": self.set_default_exit_hotkey
        })
        options.append({
            "label": "pause-hotkey",
            "description": "", 
            "get": self.get_pause_hotkey,
            "set": self.set_pause_hotkey,
            "default": self.set_default_pause_hotkey
        })
        options.append({
            "label": "save-hotkey",
            "description": "", 
            "get": self.get_save_hotkey,
            "set": self.set_save_hotkey,
            "default": self.set_default_save_hotkey
        })
        options.append({
            "label": "visible-hotkey",
            "description": "", 
            "get": self.get_visible_hotkey,
            "set": self.set_visible_hotkey,
            "default": self.set_default_visible_hotkey
        })
        return options
    
    def get_auto_start(self): 
        return self._auto_start

    def set_auto_start(self, value: bool): 
        if value in ['True', 'False', 'true', 'false', 1, 0]:
            self._auto_start = value in ['True', 'true', 1]
    
    def set_default_auto_start(self):
        self.set_auto_start(False)

    def get_output(self): 
        return self._output

    def set_output(self, value: str): 
        if value in ["local", "console", "debug"]:
            self._output = value
    
    def set_default_output(self):
        self.set_output("local")

    def get_hide(self): 
        return self._hide

    def set_hide(self, value: str): 
        if value in ["never", "ready", "instant", "always"]:
            self._hide = value
    
    def set_default_hide(self):
        self.set_hide("never")

    def get_exclude_typos(self): 
        return self._exclude_typos

    def set_exclude_typos(self, value: bool): 
        if value in ['True', 'False', 'true', 'false', 1, 0]:
            self._exclude_typos = value in ['True', 'true', 1]
    
    def set_default_exclude_typos(self):
        self.set_exclude_typos(True)

    def get_processing_time(self): 
        return self._processing_time

    def set_processing_time(self, value: int): 
        if value >= -1 and value < 3600000:
            self._processing_time = value

    def set_default_processing_time(self):
        self.set_processing_time(2000)

    def get_file_prefix(self): 
        return self._file_prefix

    def set_file_prefix(self, value: str): 
        self._file_prefix = value

    def set_default_file_prefix(self):
        self.set_file_prefix("")

    def get_combination_time(self): 
        return self._combination_time

    def set_combination_time(self, value: int): 
        if value >= 0 and value < 3600000:
            self._combination_time = value

    def set_default_combination_time(self):
        self.set_combination_time(800)

    def get_save_interval(self): 
        return self._save_interval

    def set_save_interval(self, value: int): 
        if value >= 0 and value < 3600000:
            self._save_interval = value

    def set_default_save_interval(self):
        self.set_save_interval(5000)

    def get_exit_hotkey(self): 
        return self._exit_hotkey

    def set_exit_hotkey(self, value: str): 
        self._exit_hotkey = value

    def set_default_exit_hotkey(self):
        self.set_exit_hotkey("ctrl+alt+x")

    def get_pause_hotkey(self): 
        return self._pause_hotkey

    def set_pause_hotkey(self, value: str): 
        self._pause_hotkey = value

    def set_default_pause_hotkey(self):
        self.set_pause_hotkey("ctrl+alt+p")

    def get_save_hotkey(self): 
        return self._save_hotkey

    def set_save_hotkey(self, value: str): 
        self._save_hotkey = value

    def set_default_save_hotkey(self):
        self.set_save_hotkey("ctrl+alt+s")

    def get_visible_hotkey(self): 
        return self._visible_hotkey

    def set_visible_hotkey(self, value: str): 
        self._visible_hotkey = value

    def set_default_visible_hotkey(self):
        self.set_visible_hotkey("ctrl+alt+v")


