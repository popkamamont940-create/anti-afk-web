# ⚡ Anti-AFK for Roblox – Web Edition

**Made by Jakonchik** – a simple tool to prevent AFK kick in Roblox by simulating keyboard presses (Space or WASD) with random delays.

---

## 🎮 What is this?
- When you're AFK in Roblox, the game might kick you.
- This tool presses keys automatically while you're away.
- You can choose: Space only, WASD only, or Mixed (random).
- It runs in your browser with a cool dark interface.

---

## 🖥️ For Players – How to use (step by step)

### 1. Install Python
- Go to [python.org](https://www.python.org/downloads/)
- Download Python **3.10 or newer** (any version)
- **During installation, check "Add Python to PATH"** – very important!
- Click "Install Now".

### 2. Download this tool
- On the GitHub page, click the green **"Code"** button.
- Choose **"Download ZIP"**.
- Extract the ZIP file to a folder (e.g., `Desktop\AntiAFK`).

### 3. Install required packages
- Open the extracted folder.
- Right-click inside the folder while holding **Shift** → **"Open PowerShell window here"** (or "Open command window here").
- Type this command and press Enter:
  ```bash
  pip install -r requirements.txt
```

- Wait until it finishes.

### 4. Run the app

- In the same terminal, type:

```
python anti_afk_web.py
```
- You will see a message: `Uvicorn running on http://localhost:8000`

### 5. Open the web interface

- Open your browser (Chrome, Edge, Firefox).
- Go to: **[http://localhost:8000](http://localhost:8000)**
- You will see the Anti-AFK dashboard.

### 6. Use it while playing Roblox

- In the dashboard:

- Choose **Space**, **WASD**, or **Mixed** mode.
- Set min and max interval (seconds between key presses). Example: 10–60 seconds.
- Click **START**.
- Switch to your Roblox game window (it must be active).
- The app will press keys automatically. You can see the counter go up.
- To stop, click **STOP** or press the **Spacebar** key on your keyboard.

> 🔑 **If key presses don't work in Roblox:**
Close the terminal, then right-click `anti_afk_web.py` → **Run as administrator**. Then start again.

## 📁 Files in this package

| File | What it does |
|---|---|
| `anti_afk_web.py` | The main program (everything inside one file) |
| `requirements.txt` | Tells Python what libraries to install |
| `README.md` | This instruction manual |

## ❓ Troubleshooting

| Problem | Solution |
|---|---|
| `pip is not recognized` | Python wasn't added to PATH. Reinstall Python and check "Add Python to PATH". |
| `ModuleNotFoundError: No module named 'fastapi'` | Run `pip install -r requirements.txt` again. |
| Nothing happens in Roblox | 1) Make sure the Roblox window is active (click inside the game). 2) Run the script as administrator. |
| Web page doesn't open | Make sure the terminal says `Uvicorn running on http://localhost:8000`. If not, restart. |

## ⚠️ Disclaimer

- This tool may violate Roblox Terms of Service. Use at your own risk.
- For personal/educational use only. Created by Jakonchik.

**Enjoy!** 🚀 If you like it, leave a star ⭐ on GitHub.

