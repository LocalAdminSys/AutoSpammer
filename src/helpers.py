from unidecode import unidecode
from pathlib import Path 
from os import getenv
import commentjson
import winreg
import time



def get_path(target_object: str) -> bool | str:
    """This function returns the path of the specified object.
    
    The paths are defined in the function and organized in dictionaries according to their types.
    """

    # Path of Autospammer\src folder
    current_path = Path(__file__).resolve().parent

    # Path of Autospammer (main folder)
    main_path = current_path.parent

    # The program will write the reg delete log to \Appdata\Local\Temp\, 
    # However, since I don't know the user's name, 
    # I need to query the constant environment variable.
    temp_path = getenv("TMP") 

    # region Path lists
    main_paths = {
    "main_folder":    main_path,
    "helpers"    :    __file__,
    "main"       :    fr"{current_path}\main.py",
    }

    json_paths = {
        "folder": fr"{current_path}\Langs",
        "tr_tr": fr"{current_path}\Langs\tr_TR.jsonc",
        "en_us": fr"{current_path}\Langs\en_US.jsonc",
        "nl_nl": fr"{current_path}\Langs\nl_NL.jsonc",
    }

    regcleanup_paths = {
        "folder": fr"{current_path}\RegCleanup",
        "mgr": fr"{current_path}\RegCleanup\RegCleanUp_mgr.py",
        "reg": fr"{current_path}\RegCleanUp\RegCleaner.ps1",
        "log": fr"{temp_path}\Autospammer_registry_CleanUp.log",
    }
    # endregion

    target_object = target_object.strip().lower()

    try:
        if target_object.startswith("json."):
            target_object = target_object.removeprefix("json.").replace("-", "_")
            path_target_object = json_paths[target_object]

        elif target_object.startswith("cleanup."):
            target_object = target_object.removeprefix("cleanup.")
            path_target_object = regcleanup_paths[target_object]

        else:
            path_target_object = main_paths[target_object]
    
    except KeyError:
        print("Error: There is an error in the parameter control the parameter and try again." 
              f"Incorrect parameter: '{target_object}'"
        )
        return False

    except Exception as e:
        print(f"An unknown error occured. \ndescription: {e}")
        return False
    
    return path_target_object
    



# open json file
def get_json(src: str, ALLOW_NON_ASCII: bool = False) -> dict:
    """This function finds and returns the required JSON file and the specified section."""

    # Getting current system Language
    try: 
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as reg_openkey:
            # [0]: get the value (skip the data type). As a result, the output is a list.
            # [0][0]: get the first string of the list.
            current_language = winreg.QueryValueEx(reg_openkey, "PreferredUILanguages")[0][0].replace("-", "_")
            

    except PermissionError:
        print("Access was denied while trying to access the system language." 
              "The application will be displayed in English."
        )
        current_language = 'en_US'

    except Exception as e:
        print("An unknown error occurred while getting the system language."
              f"Description: {e}\n\n"
              "The application will be displayed in English"
        )   
        current_language = 'en_US'    

    # if you want to test the application in a specific language without changing your system language, you can use this example:
    # current_language = (your desired language here, for example: "nl_NL")

    if not (json_location := get_path(f"json.{current_language}")):  # Gratitude to Tim Peters for ':='. this line exists because of you.
        print("\nYour system language is not supported. The application will be displayed in English.")
        json_location = get_path("json.en_US")

    with open(json_location, 'r', encoding= 'utf-8') as l:
        
        if ALLOW_NON_ASCII:
            asked_json = commentjson.load(l)
        
        # Getting the JSONC and converting the Unicode characters to standard characters 
        # (for example: 'ş' to 's', 'ç' to 'c', etc.)
        else:
            raw_json = l.read()
            unidecoded_json = unidecode(raw_json)
            asked_json = commentjson.loads(unidecoded_json)

    return asked_json[src]



# Function to list saves.
def list_saves() -> bool | list:
    """This function lists the existing save in the registry. 
    It is used in both 'load_save' and 'list_saves' commands.
    """

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\AutoSpammer") as key:
            sub_key_numbers = winreg.QueryInfoKey(key)[0]
            return[winreg.EnumKey(key, k) for k in range(sub_key_numbers)]
        
    except FileNotFoundError:
        return []
    
    except Exception as e:
        msg = get_json("list_saves")
        print(msg["UnknownError"].format(e = e))
        return False



# Save and load spams from the registry
def reg_save(command: str,
            messages: list = None,
            times: int | str = None,
            waiting_period: int | float | str = None,
            delays: int | float | str = 0.01,
            ) -> bool | tuple | None:
    """This function is used to save and load spams from the registry."""
    
    commands = ("list_saves", "create_save", "load_save")
    msg = get_json("reg_save")
    main_key = r"Software\AutoSpammer"

    # Returning an error from the very beginning if there are errors in the parameters.
    is_none = messages is None or times is None or waiting_period is None
    
    if command not in commands or (command == "create_save" and is_none):
        print(msg["InvalidParameterError"])
        return False

    saves = list_saves()

    # If there are no saves or an error occurs, the program should not continue the function; 
    # if the 'saves' variable is 'None' or 'False', this function should also return.
    if not saves and command != "create_save":
        return None

    match command:
        # If only existing saves are to be listed...
        case "list_saves":

            print(msg["list_saves"])
            for k, save in enumerate(saves, start=1):
                print(f"{k}: '{save}'")

            return True

        # If a save is to be loaded...
        case "load_save":
            if saves == []:
                print(msg["NoSaveError"])
                return False
            
            print(msg["list_saves"])
            for k, save in enumerate(saves, start=1):
                print(f"{k}: '{save}'")

            while True:
                loaded_save = input(msg["load_save"]).strip()
                if loaded_save.isdigit():
                    loaded_save = saves[int(loaded_save) - 1]
                    break

                print(msg["invalid_option"])
                time.sleep(0.5)

            saved_delays = 0.01  # In case there is no 'Delays' value in the registry\.
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, fr"{main_key}\{loaded_save}") as key:
                    total_values = winreg.QueryInfoKey(key)[1]   # [1]: Just get how many values ​​are in the key.

                    for v in range(total_values):
                        name, value, value_type = winreg.EnumValue(key, v)

                        match name, value_type:
                            case "Messages", winreg.REG_MULTI_SZ:
                                saved_messages = list(value)

                            case "Times", winreg.REG_DWORD:
                                saved_times = int(value)

                            case "waiting_period", winreg.REG_SZ:
                                saved_waiting_period = float(value)

                            case "Delays", winreg.REG_SZ:
                                saved_delays = float(value)
            
            except Exception as e:
                print(msg["UnknownError"].format(e = e))
                return False
            
            return (
                saved_messages,
                saved_times,
                saved_waiting_period,
                saved_delays,
            )

        # If a new save is to be created...
        case "create_save":
            while True:
                save_name = input(msg["save_name"])

                if "\\" in save_name:
                    print(msg["invalid_key_name"])
                    continue

                try:
                    # If it doesn't return a 'FileNotFoundError' here, it means there's already a save with that name.
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, fr"{main_key}\{save_name}", 0, winreg.KEY_READ):
                        pass

                    match file_exists_options := input(msg["FileExistsError"]):
                        # choose another name
                        case "1":
                            continue

                        # overwrite the current name:
                        case "2":
                            # ------------------------------------- a small complaint ----------------------------------
                            # I had a plan here: I was going to copy the existing save as a '.old' key, 
                            # and delete it only after the new save was safely created without errors. 
                            # This was meant to prevent data loss in case the creation process failed. 
                            # Unfortunately, it didn't work out. Details below...
                            #
                            # I'm very sorry, but... unfortunately, there's no command like 'winreg.rename_key'.
                            # In fact, there's no way to completely rename a registry key in Windows.
                            #
                            # Implementing a workaround with 'subprocess' and 'reg copy' introduces a much 
                            # higher risk of error than the current method and makes the code 
                            # incredibly long, fragile, and complex.
                            #
                            # With the intention of fixing this issue:
                            #   @TimPetersPleaseSolveThis
                            #   @CopyPasteDeleteIsNotRename
                            #   @NadellaPleaseAddRealRegRenameToWindows
                            # ---------------------------------------------------------------------------------------------
                            break

                        # cancel
                        case "3":
                            return None
                        
                        # Here, if the user enters something incorrectly, they will have to select the name again. 
                        # Preventing this... 
                        # I think Zen of Python wouldn't like that.
                        case _:
                            print(msg["invalid_option"])

                # If there is no save with the same name (returns FileNotFoundError), then the name is valid. Breaking out of the loop.
                except FileNotFoundError:
                    break

                except Exception as e:
                    print(msg["UnknownError"].format(e = e))
                    return False
            
            # Creating the save
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, fr"{main_key}\{save_name}") as key:
                    winreg.SetValueEx(key, "Messages", 0, winreg.REG_MULTI_SZ, messages)
                    winreg.SetValueEx(key, "Times", 0, winreg.REG_DWORD, int(times))
                    winreg.SetValueEx(key, "waiting_period", 0, winreg.REG_SZ, str(waiting_period))   # Float and str can't be written to dword, therefore using reg_sz.
                    winreg.SetValueEx(key, "CreationTime", 0, winreg.REG_SZ, time.ctime())   # Just for information, it's not used in the program.
                    if delays: winreg.SetValueEx(key, "Delays", 0, winreg.REG_SZ, str(delays))
        
            except PermissionError:
                print(msg["PermissionError"])
                return False

            except Exception as e:
                print(msg["UnknownError"].format(e = e))
                return False
            
            print(msg["successfully_saved"].format(save_name = save_name))
            return True