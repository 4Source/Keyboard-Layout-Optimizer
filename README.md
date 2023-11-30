# Keyboard Layout Optimizer

This Project is based on the [AtomicFrontierCode/keyboards](https://github.com/AtomicFrontierCode/keyboards) Repository.

You feelt like the standard keyboard layout isn't a charm? Or just wanna try Another Keyboard Layout? This Project could help you find **your** better keyboard layout. The change won't be easy, so you should think carefully about whether you want to do it. It is also important that _myBook_ contains _pages_ that are suitable for you. _myBook_? _pages_? What does that mean? _myBook_ is the name of the folder where the pages are in. The _pages_ are Text you wrote or just text in the languges you use. These text will be used to create a heatmap, this will measure the usability of the keyboard layout. 

> [!WARNING]
> This Project is still under development.

# Getting started
1. Get the Files
    - ```cd YOUR-FOLDER```
    - ```git clone https://github.com/4Source/Keyboard-Layout-Optimizer.git```
    - ```cd Keyboard-Layout-Optimizer```
2. Create _myBook_
    - Option 1 **(Recommendet)**
        1. Install Python
            - If you havend allready you need to install [Python 3](https://www.python.org/downloads/).
        2. Install Requirements
            - ```pip install ...``` see [requirements](https://github.com/4Source/Keyboard-Layout-Optimizer/blob/0559009ecdf047fd0d607f1708d0e4a9043dff64/python%20requirements.txt)
        3. Setup Keylogger
            - ```python SetupKeylogger.py```
            - Need to run once to create the config file. You can just run it and than exit or change config [[Show options](https://github.com/4Source/Keyboard-Layout-Optimizer/tree/master#configs)] if you like.
        4. Start Keylogger
            - ```python keylogger.py```
            - Let it run as long as you like. Recommendet to collect data for coulple of weeks.
            - You can also add _pages_.txt that you would like to be taken into account. If you add large files or files with just word list this can distort the result. **Solution:** Don't add them or let the keylogger collect more data.
    - Option 2
        1. Create _myBook_ folder in this folder.
        2. Add _pages_.txt manualy. Don't use only word list this can result in unusable keyboard layout. **Good options are:** Text/Code you wrote or Text/Code from Books or other sources
3. To be continued...

# Keylogger
## Why Keylogger?
This isn't a must, but if you leave it running for a few weeks while you type on your computer, you'll get a personalized keyboard layout based on your most frequently used keys. This keylogger cannot send your files to other locations, but it is **strongly recommended** to pause the keylogger using the _pause-hotkey_ while typing passwords. Your passwords wont be saved in plane text but will stay in keylogger till stopped the keylogger.
> [!Note]
> It is **strongly recommended** to pause the keylogger using the _pause-hotkey_ while typing passwords.
## Where get it saved?
Your pressed Keys **only** get saved on your local computer. You can find them in _myBook_ which get created if your first keys get logged. Inside you will find _heatmap_ with the count of pressed keys. 
## Configs
- _auto-start_
    - **False** (Default) - The Keylogger needs to be started manually.
    - **True** - The Keylogger will auto start at startup. 
- _output_
    - **local** (Default) - Key presses get logged localy on your computer.
    - **console** - Key names get printed to console. Requiers _hide_ = False.
    - **debug** - Key presses get printed to the console. Ignores _hide_ config.
- _hide_
  - **False** (Default) - Console stays visible after starting the Keylogger.
  - **True** - Console will be invisible also with _auto-start_ = True.
- _exclude-typos_
  - **True** (Default) - If you use BACKSPACE the last keys get removed from buffer.
  - **False** - Keep all keys you typed.
- _file-prefix_
  - **""** (Default) - Your files have no prefix.
  - **"YOUR-PREFIX"** - It is posible to prefix your files with a custom prefix. Usefull if you use on mulible computers and will combine all your files in one folder so you get not file name conflicts.
- _hotkeys_
  - _exit-hotkey_
    - **ctrl+alt+x** (Default) - To stop the Keylogger completly also in hidden mode.
    - **YOUR-HOTKEY** - **Only** use correct hotkeys. If you unsure how the keys are named you could use _mode_ = console to see the namings. Invalid hotkeys may crash the keylogger.
  - _pause-hotkey_
    - **ctrl+alt+p** (Default) - To Pause/Continue the Keylogger. Usefull is you don't want your passwords in the 'page' files appier in clear text.
    - **YOUR-HOTKEY** - **Only** use correct hotkeys. If you unsure how the keys are named you could use _mode_ = console to see the namings. Invalid hotkeys may crash the keylogger.
  - _save-hotkey_
    - **ctrl+alt+s** (Default) - To save the buffer. Usefull is if you wanna save the buffer manually.
    - **YOUR-HOTKEY** - **Only** use correct hotkeys. If you unsure how the keys are named you could use _mode_ = console to see the namings. Invalid hotkeys may crash the keylogger.
