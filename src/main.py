# Created and developed by LocalAdminSys.
# Licensed under MIT license

__version__ = "1.0.0"

import pyperclip   # This module writes text using the copy-paste method. (NOT RECOMMENDED).
import pyautogui
import time

from __init__ import *

# Dictionaries to avoid having to reintroduce them each time.
ACCEPTANCE = ('y', 'yes', 'yep', 'yeah', 'e', 'evet', 'j', 'ja')
REJECTION  = ('n', 'no', 'nah', 'nope', 'h', 'hayir', 'hayır', 'nee')

# Dictionary that allows to quickly find and change the limits.
LIMITS = {
        # Max/min delay between each message.
        "delays": {
            "AT_LEAST": 0,
            "AT_MOST": 99
        },

        # Max/min different messages.
        "introduction": { 
            "AT_LEAST": 1,
            "AT_MOST": 99
        },

        # Max/min number of times each message can be written
        "last_selections.writing_amount": {
            "AT_LEAST": 1,
            "AT_MOST": 99
        },

        # Max/min time to wait after everything is ready and the Enter key is pressed.
        "last_selections.delay": {
            "AT_LEAST": 0,
            "AT_MOST": 99
        }
}

# list to save the messages.
message_list = []

# region variables and constants

# Allowing the user to change some settings.

ALLOW_WAIT = True   # Allow short pauses between messages and questions (this has no effect on spamming).
ALLOW_LIMITS = True   # Allow maximum and minimum limits (CHANGING NOT RECOMMENDED).
ALLOW_DELAYS = False   # Allow the 'delay' feature. (This means an extra question will be asked)
ALLOW_RESTART = True   # Allow the "again?" question after the spam is completed.
ALLOW_SAVE_SPAM_QUESTION = True   # Allow the question "Do you want to save this spam?" after the spam is completed.

ALLOW_NON_ASCII = False  # Allow Non-ASCII (Unicode) characters. Default is False.
                         # NOTE: This setting has no function in English and Dutch.

MOVETO_NEXT_LINE = False   # Instead of sending the messages, move to the next line. (use shift + enter)
USE_COPY_PASTE_SYSTEM = False   # Copy and paste the message instead of typing it directly (NOT RECOMMENDED).

msg = get_json(src="main.py", ALLOW_NON_ASCII=ALLOW_NON_ASCII)
print(msg["language_selected"])

# endregion 



# region function definitions:

cls = lambda: print("\033c")   # This function clears the console.

# According to the limit dict, it returns a result (bool or str).
def limit_mgr(source: str,  value: int, only_info: bool = False) -> bool | str:     
    """According to the limits dict, returns the result.

    According to the limits dict, ALLOW_LIMITS constant and the given value,
    returns the result or the desired limit.

    If you want to disable the limits (NOT RECOMMENDED), 
    change the 'ALLOW_LIMITS' constant to False or None.
    """

    if ALLOW_LIMITS and only_info:
        return f"({LIMITS[source]['AT_LEAST']}-{LIMITS[source]['AT_MOST']})"

    elif only_info:
        return "(∞-∞)"
    
    elif ALLOW_LIMITS:
        return LIMITS[source]["AT_LEAST"] <= value <= LIMITS[source]["AT_MOST"]  # returns bool
    return True


# function to better control waiting times.
def wait(time_in_seconds: int) -> bool:
    """function to better control waiting times.
    
    If you want to disable waiting times, 
    Change the value "ALLOW_WAIT = True" to False or None. 
    """

    if ALLOW_WAIT:
        time.sleep(time_in_seconds)
    return True


# It asks for the time interval between each message.
def delays() -> float:
    """It asks for the time interval between each message.

    Ask the user if there should be a delay between each message 
    (this is optional and off by default. 
    To enable it, set ALLOW_DELAYS = False to True).
    """

    while ALLOW_DELAYS:
        delay = input(msg["delay_question"] + f"{limit_mgr(source="delays", 
                                                           value=00, 
                                                           only_info=True)}"
                                                           ).strip()
        try:
            delay = float(delay)
            if limit_mgr(source="delays", value=delay):
                return delay
            raise ValueError

        except:
            print(msg["invalid_option"] + "\n\n")
            wait(0.5)

    # NOTE: This delay is to prevent lag. You can change it. 
    # You can set it to 0 or any number you want, 
    # but DO NOT DELETE THIS LINE.
    return 0.01
    

# This function is where the user selects how many different messages they want to send
def introduction() -> int: 
    """It asks how many different messages to send.
    
    The valid inputs at this stage are:

    a number that meets the limits:
        Learns how many different messages to send and continues.
    'saves':
        Shows all spams registered in the registry.
    'version':
        States the current version.
    'exit' / 'quit':
        Exits the program
    'delete':
        Opens the registry cleanup manager, where you can delete registry key(s) created by the program.
    """

    while True:
        different_msg_amount = input(msg["different_msg_question"].format(limits = limit_mgr(source="introduction", 
                                                                                             value=00, 
                                                                                             only_info=True))
                                                                                             ).lower().strip()
        match different_msg_amount:
            case "saves" | "kayitlar" | "kayıtlar" | "records":
                try:
                    messages, writing_amount, waiting_period, delay = reg_save(command="load_save")
                
                # I added these lines to prevent the program from crashing if the 'reg_save' func returns 'False' 
                # due to an error. No further explanation is needed as it's already explained in the reg_save func.
                except:
                    pass

                else:
                    message_list.extend(messages)
                    start(writing_amount=writing_amount, waiting_period=waiting_period, delay=delay)
                    restart(writing_amount=writing_amount, waiting_period=waiting_period, delay=delay)

            case "version" | "versiyon" | "versie":
                cls()
                print(msg["__version__"].format(version = __version__))
                wait(1.5)
                continue

            case "exit" | "quit" | "çıkış" | "kapat" | "afsluiten":
                cls()
                print(msg["quit_txt"])
                wait(1)
                raise SystemExit(0)

            case "delete" | "sil" | "verwijderen":
                RegCleanUp_mgr.registry_cleanup_mgr()
                continue

            case _:
                try:
                    different_msg_amount = int(different_msg_amount)
                    if limit_mgr(source="introduction", value=different_msg_amount):
                        print(msg["amount_info"].format(different_msg_amount = different_msg_amount))
                        return different_msg_amount
                    raise ValueError
                
                except:
                    cls()
                    print(msg["list_commands"])
                    wait(3)


# This function is where the user selects what will be written in each message.
def message_selection(different_msg_amount: int) -> bool:
    """It asks the user what to write in each message."""
    # ====================================================================================================
    # NOTE: The symbols and emojis (?, /, \, $, #, etc...) don't work correctly because 
    # typing them requires extra keys (shift, alt) on some keyboard layouts,
    # and when I try to type them with PyAutoGUI, the correct symbols aren't displayed. 
    # I don't know a clean solution but there's no crashing, just the wrong symbols are being typed.
    #
    # It's not a clean method, but if you want, 
    # you can set the "USE_COPY_PASTE_SYSTEM = False" constant to "True" at the beginning of the code.
    #
    # This method uses copy-paste instead of typing words directly, 
    # which clutters the clipboard.
    #                                       (NOT RECOMMENDED)
    # ====================================================================================================
    cls()
    print(msg["msg_preparation"].format(different_msg_amount = different_msg_amount))

    for m in range(different_msg_amount):
       add = input(msg["msg_no"].format(msg_no = m + 1))
       message_list.append(add)
    return True



# Asking the user various questions about how the spam will be.
def last_selections() -> tuple[int, float, float]:
    """This function asks the user various questions;
    
    1) How many times in total will each message be written?
    2) What will the delay be between each message? (optional)
    3) Once everything is ready, how many seconds later will the spam start?
    """

    cls()
    
    # asking the user how many times they want each message to be written in total.
    while True:
        writing_amount = input(msg["writing_amount_question"].format(limits = limit_mgr(source="last_selections.writing_amount", 
                                                                                        value=00, 
                                                                                        only_info=True))
                                                                                        ).strip().replace(",", ".")
        try:
            writing_amount = int(writing_amount)
            if limit_mgr(source="last_selections.writing_amount", value=writing_amount):
                break
            raise ValueError
        
        except:
            print(msg["invalid_option"])
            wait(0.5)

    # Ask the user if there should be a delay between each message 
    # (this is optional and off by default. To enable it, set ALLOW_DELAYS = False to True).
    delay = delays()   

    # asking the user how many seconds they want before the spam starts.
    while True:
        waiting_period = input(msg["start_delay_question"].format(limits = limit_mgr(source="last_selections.delay", 
                                                                                     value=00, 
                                                                                     only_info=True))
                                                                                     ).strip().replace(",", ".")
        try:
            waiting_period = float(waiting_period)

            if limit_mgr(source="last_selections.delay", value=waiting_period):
                return writing_amount, waiting_period, delay
            raise ValueError
        
        except:
            print(msg["invalid_option"])
            wait(0.5)



# The function where the spam starts.
def start(writing_amount: int, waiting_period: int | float, delay: int | float) -> bool:
    """The function where the spam occurs."""

    cls()
    input(msg["ready_txt"].format(waiting_period = waiting_period, 
                                  total_msg = (len(message_list) * writing_amount)))
    
    cls()
    print(msg["start"].format(waiting_period = waiting_period))

    time.sleep(waiting_period)

    # if the 'directly writing' system is being used.
    if not USE_COPY_PASTE_SYSTEM:
        # if the 'send the message' option is being used.
        if not MOVETO_NEXT_LINE:
            for _ in range(writing_amount):
                for m in (message_list):
                    pyautogui.write(m, interval=0.01)
                    pyautogui.press("enter")
                    time.sleep(delay)
            return True
        
        # if the 'move to the next line' option is being used.
        for _ in range(writing_amount):
            for m in (message_list):
                pyautogui.write(m, interval=0.01)
                pyautogui.hotkey('shift', 'enter')
                time.sleep(delay)
        return True
    
    # If the 'copy-paste' system is being used.
    elif USE_COPY_PASTE_SYSTEM:
        # if the 'send the message' option is being used.
        if not MOVETO_NEXT_LINE:
            for _ in range(writing_amount):
                for m in (message_list):
                    pyperclip.copy(m)
                    pyautogui.hotkey('ctrl', 'v')
                    pyautogui.press("enter")
                    time.sleep(delay)
            return True
    
        # if the 'move to the next line' option is being used.
        for _ in range(writing_amount):
            for m in (message_list):
                    pyperclip.copy(m)
                    pyautogui.hotkey('ctrl', 'v')
                    pyautogui.hotkey('shift', 'enter')
                    time.sleep(delay)
        return True



# Asking the user if they want to save the spam in the registry.
def save_spam_func() -> bool |None:
    """This function asks the user if they want to save the spam in the registry."""

    while ALLOW_SAVE_SPAM_QUESTION:
        save_spam = input(msg["reg_save_question"]).strip().lower()

        if save_spam in ACCEPTANCE:
            return True

        elif save_spam in REJECTION:
            return None

        print(msg["invalid_option"]) 
        wait(0.5)



# asking the user if they want another round with the same spam.
def restart(writing_amount: int, waiting_period: int | float, delay: int | float):
    """This function asks the user if they want to restart the spam."""

    while ALLOW_RESTART:
        again = input(msg["again_question"]).strip().lower()
        
        if again in ACCEPTANCE:
            start(writing_amount, waiting_period, delay)
            continue

        elif again in REJECTION:
            print(msg["quit_txt"])
            wait(1)
            raise SystemExit(0)
        
        print(msg["invalid_option"])
        wait(0.5)

# endregion Functions



# region main code:

message_selection(introduction())

writing_amount, waiting_period, delay = last_selections()

start(writing_amount=writing_amount, 
      waiting_period=waiting_period, 
      delay=delay)

if save_spam_func():
    reg_save(command="create_save", 
             messages=message_list, 
             times=writing_amount, 
             waiting_period=waiting_period, 
             delays=delay)

restart(writing_amount=writing_amount, 
        waiting_period=waiting_period, 
        delay=delay)

# endregion main code