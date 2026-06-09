import subprocess
import time

from __init__ import *


msg = get_json("RegCleanUp_mgr.py")

# If you don't want to accidentally delete the reg saves.
SAFE_MODE = False

ACCEPTENCE = ('y', 'yes', 'yep', 'yeah', 'e', 'evet', 'j', 'ja')
REJECTION = ('n', 'no', 'nah', 'nope', 'h', 'hayir', 'hayır', 'nee')

# Manager function
def registry_cleanup_mgr() -> bool:
    """It calls the appropriate registry cleaner function requested by the user."""

    print(msg["cleanup_options"])
    
    while True:
        match choice := input(msg["your_choice"]).strip():
            case "1":
                result = registry_cleanup("\\main\\")   # To avoid confusion with save names, using the '\' symbol.
                return result

            case "2": 
                if saves := list_saves():
                    print(msg["saves_list"])

                    # Numbers each save as 1, 2, 3... and states the name of each save. For Example: 1: 'MySave'
                    for k, save in enumerate(saves, start=1):
                        print(f"{k}: '{save}'")

                    while True:
                        target_key = input(msg["enter_save_number"]).strip()
                        if target_key.isdigit():
                            target_key = int(target_key) - 1

                            result = registry_cleanup(saves[target_key])
                            return result
                        
                        print(msg["invalid_option"])
                print(msg["no_save_found"])
                return False
                        
            case "3":
                print(msg["operation_cancelled"])
                return None
            
            case _:
                print(msg["invalid_option"])



# Registry cleanup
def registry_cleanup(target_key: str) -> bool:
    """It deletes registry keys using powershell script.

    The specified registry key is deleted using 
    the 'RegCleaner.ps1' file located in the same folder.
    """

    if SAFE_MODE:
        print(msg["SAFE_MODE"])
        return None



    def approving(key) -> bool:
        """This function asks the user for approval before deleting the registry key."""

        if key == "\\main\\":
            key = "HKCU\\Software\\AutoSpammer (main key)"

        else:
            key = f"HKCU\\Software\\AutoSpammer\\{key}"

        while True:
            approve = input(msg["approve_deletion"].format(key = key)).strip().lower()

            if approve in ACCEPTENCE:
                return True
            
            elif approve in REJECTION:
                print(msg["operation_cancelled"])
                return None
            
            print(msg["invalid_option"])



    if approving(target_key):
        print(msg["powershell_script_running"])
        try:
            subprocess.run(["Powershell",                 # script language
                           "-ExecutionPolicy", "Bypass",  # Preventing the script from being blocked due to ExecutionPolicy.
                           "-File",                       # Specifying that it will run a script, not code.
                           get_path('cleanup.reg'),     # Script Path
                           target_key],                   # Parameter
                           check=True                     # If an error occurs, it will be indicated.
            )
        
        except subprocess.CalledProcessError:
            print(msg["SubprocessError"].format(log_file = get_path("cleanup.Log")))
            return False

        except FileNotFoundError:
            print("FileNotFoundError")
            return False

        except Exception as e:
            print(msg["UnknownError"].format(e = e))
            return False
        
        print(msg["successfully_deleted"].format(log_file = get_path("cleanup.Log")))
        return True
    
    return None

    