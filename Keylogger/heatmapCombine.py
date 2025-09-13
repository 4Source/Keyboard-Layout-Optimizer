import json
import os
from os.path import join, getsize
import sys

# Folder where the pages of your book get logged
BOOK_PATH = 'myBook'
# Directory path
DIR_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

# Buffer for Heatmap
heatmap_buffer = {
    "total": {
        "mentions": 0
    }
}

def combine(buffer):
    global heatmap_buffer
    if not hasattr(buffer, 'items') or not callable(getattr(buffer, 'items')):
        raise Exception('Buffer missing callable items')
    for k,v in buffer.items():
        if k in heatmap_buffer:
            heatmap_buffer[k]["mentions"] = heatmap_buffer[k]["mentions"] + buffer[k]["mentions"]
        else:
            heatmap_buffer[k] = buffer[k]
        heatmap_buffer["total"]["mentions"] = heatmap_buffer["total"]["mentions"] + buffer[k]["mentions"]

def combine_json():
    skippedCount = 0
    removedCount = 0
    fixedCount = 0
    errorCount = 0
    totalCount = 0
    path = join(DIR_PATH, os.pardir, BOOK_PATH)
    for file in os.listdir(path):
        filePath = join(path, file)
        try:
            if file.endswith("json"):
                totalCount = totalCount + 1
                if file == "final.heatmap.json":
                    skippedCount = skippedCount + 1
                    continue
                if file.endswith(".heatmap.json"):
                    if getsize(filePath) == 0:
                        print("Removed empty file: " + file)
                        os.remove(filePath)
                        removedCount = removedCount + 1
                        continue
                    try:
                        with open(filePath, "r") as read_file:
                            temp_buffer = json.load(read_file)
                            combine(temp_buffer)
                    except json.JSONDecodeError as error:
                        print("JSON decode error in file " + file + ", trying to fix...")
                        errorCount = errorCount + 1
                        with open(filePath, "r") as read_file:
                            broken_data = read_file.read()

                        fixed_data = json.loads(broken_data + "\n}")
                        combine(fixed_data)
                        with open(filePath, "w") as write_file:
                            json.dump(fixed_data, write_file, indent=4)
                        fixedCount = fixedCount + 1
                        print("Fixed file: " + file)

                if file.endswith(".list.json"):
                    skippedCount = skippedCount + 1
                    continue
        except Exception as error:
            print(repr(error) + ' in File: ' + file)
            errorCount = errorCount + 1
    print("Processed files (" + str(totalCount - skippedCount - errorCount - removedCount) + "/" + str(totalCount) + ")")
    print("Fixed files (" + str(fixedCount) + "/" + str(errorCount) + ")")
    print("Canceled files (" + str(errorCount) + "/" + str(totalCount) + ")")
    print("Removed files (" + str(removedCount) + "/" + str(totalCount) + ")")

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
    print("Combine heatmap completed.")
    print("Result in 'final.heatmap.json'")

main()