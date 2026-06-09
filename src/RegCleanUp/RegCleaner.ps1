# LocalAdminSys\AutoSpammer Registry cleaner powershell script.

# Get the parameter
param (
    [string]$key
)

# variables
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$log_file = "$env:TMP\AutoSpammer_registry_CleanUp.log"
$path = "HKCU:\Software\AutoSpammer"

# Starting log 
"$time The Registry cleanup process has begun." | Add-Content -Path "$log_file"

# Check if the parameter is NOT none
if ([string]::IsNullOrWhiteSpace($key)) {
    "The parameter was returned empty. The system locked itself for security reasons." | Add-Content -Path "$log_file"
    exit
}

# Functions

# If only a specific key is to be deleted...
function specified_key {
    try {
        Remove-Item -Path "$path\$key" -Recurse -Force -ErrorAction Stop
        "$time The key: $path\$key has been successfully deleted." | Add-Content -Path "$log_file"
    }
    catch {
        # The command '$_.Exception.Message' gets the details of the error.
        $error_desc = $_.Exception.Message
        "$time An error occurred while attempting to delete the $path\$key registry key. Details: $error_desc" | Add-Content -Path "$log_file"
    }
}

# If the main key is to be deleted...
function main_key {
    try {
        Remove-Item -Path "$path" -Recurse -Force -ErrorAction Stop
        "$time The key: $path has been successfully deleted." | Add-Content -Path "$log_file"
    }
    catch {
        # The command '$_.Exception.Message' gets the details of the error.
        $error_desc = $_.Exception.Message
        "$time An error occurred while trying to delete the main registry key ($path). Details: $error_desc" | Add-Content -Path "$log_file"
    }
}


# If the parameter is "\main\", call the function to delete the main key; 
# else, call the function to delete a specific key.
if ($key -eq "\main\") {
    main_key
} else {
    specified_key
}

# End log.
"The registry cleaning process is complete." | Add-Content -Path "$log_file"

exit