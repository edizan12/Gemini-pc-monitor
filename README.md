#  AI System Monitor (Powered by Gemini)

An independent PC health monitor that reads real-time hardware data (CPU, RAM, disk, GPU, temperature, top processes) and sends it to **Gemini AI**, letting the model itself decide whether anything is wrong — no hardcoded thresholds involved.

## What makes this different?

Most system monitoring tools rely on **fixed thresholds** (e.g. `if disk_usage > 90: warn()`). This project intentionally does not.

The script only collects **raw data** (CPU %, RAM %, disk usage %, GPU status, top 3 resource-hungry processes) and sends it as-is to Gemini:

> "Here's the raw data. Use your own expertise to decide if there's a problem."

There is no `if % > 90` rule anywhere in the code. The model decides, using its own judgment, what counts as a critical CPU/RAM/disk level, and starts its response with either `DANGER:` or `NORMAL:`. The script reads that label and triggers a desktop notification if needed.

## How it works

```
┌──────────────────┐     ┌────────────────────┐     ┌──────────────────────┐
│  Hardware data     │ ──> │   Gemini analysis    │ ──> │  Desktop notification  │
│ (psutil/GPUtil)    │     │  (LLM makes the call) │     │   (if DANGER)          │
└──────────────────┘     └────────────────────┘     └──────────────────────┘
        │                                                       
        └── repeats every N seconds (loop) ──────────────────────┘
```

1. **Data collection** — `psutil` and `GPUtil` read CPU, RAM, disk, temperature, and GPU stats, plus the top 3 active processes.
2. **AI evaluation** — This raw data is sent to Gemini (`gemini-flash-latest`), which makes its own judgment call.
3. **Notification** — If the model says `DANGER`, a desktop notification fires. If `NORMAL`, it's just logged to the console.
4. The loop repeats at a set interval (5 seconds for testing, 600 seconds / 10 minutes recommended for normal use).

##  Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

##  API Key

This project needs a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

You do **not** need to edit any file to set it up. When you run the script, it will simply ask for your key in the terminal:

```
Enter your Google AI Studio API key: 
```

Your key is never written to disk or hardcoded anywhere in the code — it only lives in memory for the current session.

##  Usage

```bash
python Go.py
```

Press `Ctrl+C` to stop.

##  Example Output

```
=== Independent AI System Monitor Started ===
Testing connection...

[Gemini Report] -> DANGER: Disk usage on C and D drives has exceeded 98%,
which could lead to system instability — free up space by clearing
temporary files immediately.
--------------------------------------------------
[Gemini Report] -> NORMAL: System load is currently low and all resources
are within healthy ranges.
--------------------------------------------------
```

##  Tech Stack

- [Google Gemini API](https://ai.google.dev/) (`gemini-flash-latest`) — analysis and decision engine
- [psutil](https://github.com/giampaolo/psutil) — CPU/RAM/disk data
- [GPUtil](https://github.com/anderskm/gputil) — GPU data (NVIDIA GPUs)
- [plyer](https://github.com/kivy/plyer) — cross-platform desktop notifications

## ⚠️ Known Limitations

- Currently built for **Windows** (disk path formatting and notification behavior are Windows-oriented).
- `GPUtil` reliably detects only NVIDIA GPUs; integrated (Intel/AMD) GPUs may not show up.
- This tool monitors **current resource usage** only. It does not check disk physical health (SMART data), past system errors (Event Viewer), or malware.
- Gemini's free tier quota and model names can change over time; using the `gemini-flash-latest` alias reduces (but doesn't eliminate) this risk.

##  License

MIT — free to use, modify, and share.

## 🤝 Contributing

Pull requests are welcome, especially for:
- macOS/Linux support
- Historical data / trend tracking
- A simple GUI (tkinter/streamlit)
