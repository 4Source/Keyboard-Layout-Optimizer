import json
import os
from os.path import join
import sys

# Folder where the pages of your book get logged
BOOK_PATH = 'myBook'
# Directory path
DIR_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

# Buffer for Heatmap
heatmap_buffer = {}

def combine(buffer):
    global heatmap_buffer
    for k,v in buffer.items():
        if k in heatmap_buffer:
            heatmap_buffer[k]["mentions"] = heatmap_buffer[k]["mentions"] + buffer[k]["mentions"]
        else:
            heatmap_buffer[k] = buffer[k]

def combine_json():
    path = join(DIR_PATH, BOOK_PATH)
    for file in os.listdir(path):
        if file == "heatmap.final.json":
            continue
        if file.endswith("json"):
            with open(join(path, file), "r") as read_file:
                temp_buffer = json.load(read_file)
                combine(temp_buffer)

def combine_page():
    path = join(DIR_PATH, BOOK_PATH)
    for file in os.listdir(path):
        if file.endswith("txt"):
            with open(join(path, file), "r") as read_file:
                temp_buffer = {}
                for l in read_file:
                    for c in l:
                        name = c
                        if c == " ":
                            name = "space"
                        if c == "\n":
                            name = "enter"

                        if name in temp_buffer and "mentions" in temp_buffer[name]:
                            temp_buffer[name]["mentions"] = temp_buffer[name]["mentions"] + 1
                        else:
                            temp_buffer[name] = {
                                "name": name,
                                "value": c,
                                "mentions": 1
                            }
                combine(temp_buffer)

def save_heatmap():
    global heatmap_buffer
    path = join(DIR_PATH, BOOK_PATH)     
    unused = []
    for k,v in heatmap_buffer.items():
        if v["mentions"] == 0:
            unused.append(k)
    for k in unused:
        del heatmap_buffer[k]    
    file = join(path,  "heatmap.final.json")
    with open(file, "w") as write_file:
        json.dump(heatmap_buffer, write_file, indent=4)
                

def main():
    print("Started combine heatmap...")
    combine_json()
    combine_page()
    save_heatmap()
    print("Combine heatmap completted.")
    print("Result in 'heatmap.final.json'")

main()