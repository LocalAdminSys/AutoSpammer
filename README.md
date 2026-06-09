# Windows Automation & Registry Integration Project (AutoSpammer)

A personal learning project developed to explore Python's capabilities in OS-level automation, Windows Registry (`winreg`) operations, and PowerShell integration.

---

## 💡 Project Purpose

This application was built as a hands-on exercise to practice software architecture, multi-language localization, and Windows subsystem communication. 

The tool serves a simple purpose: It takes any number of custom text inputs from the user and types them sequentially at a user-defined speed. While Python is traditionally not the primary choice for native OS automation, this project explores its boundaries when combined with PowerShell.

## ✨ Technical Mechanics

* **Text Input & Emulation:** Simulates keyboard typing sequences. Includes an option to switch between standard typing (`pyautogui`) and clipboard pasting (`pyperclip`) to test layout compatibility.
* **Registry Storage:** Uses the native `winreg` API to save and load user settings and message histories directly inside the Windows Registry.
* **PowerShell Execution:** Triggers a background `.ps1` script via Python's `subprocess` to handle recursive registry subkey deletions, bypassing standard empty-key constraints.
* **Localization Engine:** Reads the native OS UI language (`PreferredUILanguages`) from the registry to dynamically load JSONC translation blueprints (English, Dutch, Turkish).

## 📂 Project Structure

```text
src/
├── Langs/                # JSONC Localization blueprints (en_US, tr_TR, nl_NL)
├── RegCleanUp/           # Registry management core
│   ├── __init__.py       # Handles internal package exposure and initialization
│   ├── RegCleanUp_mgr.py # Subprocess orchestrator for PowerShell
│   └── RegCleaner.ps1    # Forced recursive subkey purging script
├── __init__.py           # Root package exposure and re-exports
├── helpers.py            # Global environment paths, winreg handlers, and JSON parsers
├── main.py               # Main terminal interaction engine
└── runner.py             # Bootstrapper startup routine
```

## 🚀 How to Run

### Prerequisites
* **OS:** Windows 10 / 11
* **Environment:** Python 3.10+
* **Permissions:** Administrator privileges may be needed for PowerShell execution policies.

### Execution
1. Clone or download the repository.
2. Launch the application via the bootstrapper:
   ```bash
   python src/runner.py
   ```

## 🎮 Available Terminal Commands

The application accepts integer values to set limits, alongside these global utility commands:
* `saves` / `records` / `kayitlar` : Fetches saved routines from the registry.
* `delete` / `sil` / `verwijderen` : Executes the PowerShell script to clear registry records.
* `version` / `versiyon` / `versie` : Shows current build metadata.
* `exit` / `quit` / `kapat` : Safely terminates the script.

## 📜 License

Distributed under the **MIT License**. Feel free to review the source code.

---
*Developed by LocalAdminSys.*