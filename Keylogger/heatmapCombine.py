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
    if not hasattr(buffer, 'items') or not callable(getattr(buffer, 'items')):
        raise Exception('Buffer missing callable items')
    for k,v in buffer.items():
        if k in heatmap_buffer:
            heatmap_buffer[k]["mentions"] = heatmap_buffer[k]["mentions"] + buffer[k]["mentions"]
        else:
            heatmap_buffer[k] = buffer[k]

def combine_json():
    skipped = 0
    total = 0
    path = join(DIR_PATH, os.pardir, BOOK_PATH)
    for file in os.listdir(path):
        if file.endswith("json"):
            total = total + 1
            if file == "final.heatmap.json":
                skipped = skipped + 1
                continue
            if file.endswith(".heatmap.json"):
                with open(join(path, file), "r") as read_file:
                    temp_buffer = json.load(read_file)
                    try:
                        combine(temp_buffer)
                    except Exception as error:
                        print(repr(error) + ' in File: ' + file)
            if file.endswith(".list.json"):
                skipped = skipped + 1
                continue
    print("Json files (" + str(total - skipped) + "/" + str(total) + ")")

def combine_page():
    skipped = 0
    total = 0
    path = join(DIR_PATH, os.pardir, BOOK_PATH)
    for file in os.listdir(path):
        if file.endswith("txt"):
            total = total + 1
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
    print("Text files (" + str(total - skipped) + "/" + str(total) + ")")
            

def save_heatmap():
    global heatmap_buffer
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
    file = join(path,  "final.heatmap.json")
    with open(file, "w") as write_file:
        json.dump(heatmap_buffer, write_file, indent=4)
                

def main():
    print("Started combine heatmap...")
    combine_json()
    combine_page()
    save_heatmap()
    print("Combine heatmap completted.")
    print("Result in 'final.heatmap.json'")

main()