#  Independent AI System Monitor (Gemini Powered)

An independent PC health monitor that reads real-time hardware data (CPU, RAM, disk, GPU, temperature, top processes) and sends it to **Gemini AI**, letting the model itself decide whether anything is wrong — no hardcoded thresholds involved.

##  What makes this different?

Most system monitoring tools rely on **fixed thresholds** (e.g., `if disk_usage > 90: warn()`). This project intentionally does not.

The script only collects **raw data** (CPU %, RAM %, disk usage %, GPU status, top 3 resource-hungry processes) and sends it as-is to Gemini:

> "Here's the raw data. Use your own expertise to decide if there's a problem."

There is no `if % > 90` rule anywhere in the code. The model decides, using its own judgment, what counts as a critical CPU/RAM/disk level, and starts its response with either `DANGER:` or `NORMAL:`. The script reads that label and triggers a desktop notification if needed.

##  How it works



```
┌──────────────────┐     ┌────────────────────┐     ┌──────────────────────┐
│  Hardware data     │ ──> │   Gemini analysis    │ ──> │  Desktop notification  │
│ (psutil/GPUtil)    │     │  (LLM makes the call) │     │   (if DANGER)          │
└──────────────────┘     └────────────────────┘     └──────────────────────┘
        │                                                       
        └── repeats every N seconds (loop) ──────────────────────┘
```

1. **Data collection** — `psutil` and `GPUtil` read CPU, RAM, disk, temperature, and GPU stats, plus the top 3 active processes.
2. **AI evaluation** — This raw data is sent to Gemini via the authentic **Google GenAI SDK**, leveraging the infrastructure-forced `gemini-3.6-flash` model to perform an intelligent status analysis.
3. **Notification** — If the model says `DANGER`, a desktop notification fires. If `NORMAL`, it's just logged to the console.
4. **Loop execution** — The loop repeats at a set interval (`CHECK_INTERVAL_SECONDS = 5` for testing, `60` seconds or more recommended for production use).

## Installation

```bash
# Clone the repo
git clone https://github.com/edizan12/Gemini-pc-monitor.git
cd Gemini-pc-monitor

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

##  API Key

This project needs a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).

You do **not** need to edit any file or expose your credentials to set it up. For your security, the key is never hardcoded or written to disk. When you run the script, it will simply request your key in the terminal at runtime:

```text
Enter your Google AI Studio API key: 
```

The key only lives securely in volatile memory for the duration of the current terminal session.

##  Usage

```bash
python main.py
```

Press `Ctrl+C` to stop.

##  Example Output

```text
=== Independent AI System Monitor Started ===
Testing connection...

[Gemini Report] -> DANGER: Disk usage on C and D drives has exceeded 98%, which could lead to system instability — free up space by clearing temporary files immediately.
--------------------------------------------------
[Gemini Report] -> NORMAL: System load is currently low and all resources are within healthy ranges.
--------------------------------------------------
```

##  Tech Stack

* [Google GenAI SDK](https://github.com) (`gemini-3.6-flash`) — Core analysis, decision engine, and automated error handling (built-in retries for 429/503 states)
* [psutil](https://github.com/giampaolo/psutil) — System CPU, RAM, temperature, and disk analytics data
* [GPUtil](https://github.com/anderskm/gputil) — Live GPU processing and memory diagnostics (NVIDIA hardware)
* [plyer](https://github.com/kivy/plyer) — Cross-platform native desktop warning notifications

##  Known Limitations

* **OS Focus:** Currently optimized for **Windows** (disk path formatting and notification behavior are Windows-oriented). `psutil.sensors_temperatures()` is bypassed on Windows targets due to OS platform architecture limits.
* **GPU Scope:** `GPUtil` reliably detects NVIDIA GPUs; integrated chips (Intel/AMD) will return a "No GPU detected" state gracefully.
* **Scope Limits:** This tool monitors **current live resource usage** only. It does not check hard drive physical life (SMART data), past error registries (Event Viewer), or background malware.

##  License

MIT — free to use, modify, and share.

##  Contributing

Pull requests are highly welcome, especially for adding:
* Native macOS/Linux system support
* Long-term historical data analytics / structural trend tracking
* A lightweight GUI (tkinter/streamlit)
