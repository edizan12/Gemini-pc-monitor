import time
import psutil
import GPUtil
from google import genai
from google.genai import errors
from plyer import notification

# --- SETTINGS ---
# For your security, the API key is never hardcoded. It is requested at runtime.
# Get a free key at: https://google.com
GEMINI_API_KEY = input("Enter your Google AI Studio API key: ").strip()

if not GEMINI_API_KEY:
    print("Error: API key cannot be empty. Exiting.")
    exit(1)

# Authentic Google GenAI SDK client initiation
client = genai.Client(api_key=GEMINI_API_KEY)

# How often to check the system, in seconds. (Recommended: 60 seconds or more)
CHECK_INTERVAL_SECONDS = 5


def get_top_resource_hogs():
    """Lists the top 3 most active background processes by CPU usage."""
    process_list = []
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
        try:
            process_list.append({
                "App": proc.info['name'],
                "CPU_(%)": proc.info['cpu_percent'],
                "RAM_(%)": round(proc.info['memory_percent'], 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    top_cpu = sorted(process_list, key=lambda x: x['CPU_(%)'], reverse=True)[:3]
    return [{"App": x["App"], "CPU_(%)": x["CPU_(%)"], "RAM_(%)": x["RAM_(%)"]} for x in top_cpu]


def get_system_status():
    """Collects raw hardware metrics: CPU, RAM, disk, temperature, and GPU."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent

    disks = {}
    for partition in psutil.disk_partitions():
        if partition.fstype:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                drive_name = partition.device.replace(':\\', '').replace(':', '')
                disks[f"Disk_{drive_name}"] = f"{usage.percent}% full"
            except (PermissionError, OSError):
                pass

    temperatures = {}
    try:
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            for entry in entries:
                temperatures[f"{name}_{entry.label or 'Temp'}"] = f"{entry.current}°C"
    except AttributeError:
        # psutil.sensors_temperatures() is generally not supported on Windows.
        pass

    gpu_status = {}
    try:
        gpus = GPUtil.getGPUs()
        for i, gpu in enumerate(gpus):
            gpu_status[f"GPU_{i}_{gpu.name}"] = {
                "Usage_(%)": round(gpu.load * 100, 1),
                "VRAM_(%)": round(gpu.memoryUtil * 100, 1),
                "Temperature": f"{gpu.temperature}°C"
            }
    except Exception:
        # GPUtil may fail on systems without an NVIDIA GPU/driver.
        pass

    return {
        "CPU_Usage": f"{cpu}%",
        "RAM_Usage": f"{ram}%",
        "Disk_Status": disks,
        "Temperature_Sensors": temperatures if temperatures else "No data available",
        "GPU_Status": gpu_status if gpu_status else "No GPU detected"
    }


def run_ai_analysis(hardware_data, active_processes):
    """Sends raw metrics to Gemini and processes the response using the mandatory model."""
    prompt = f"""
    You are an independent AI system agent monitoring a computer's hardware in real-time.
    Analyze the following raw system metrics and most active background processes using your own judgment:

    [SYSTEM METRICS]
    {hardware_data}

    [MOST ACTIVE PROCESSES]
    {active_processes}

    Based entirely on your own expertise, decide if there is any critical issue, bottleneck, high temperature, or memory leak.
    Your response MUST start with one of these two labels based on your decision:

    1. If you detect a performance issue or risk, start your response with 'DANGER:' and write a 1-sentence smart warning and solution.
    2. If you decide the system is perfectly stable and healthy under this load, start your response with 'NORMAL:' and write a 1-sentence summary of the system status.

    Do not add any introductory greetings, meta-commentary, or markdown code blocks. Just start directly with the label.
    """

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            # FIXED: Updated to 'gemini-3.6-flash' as explicitly forced by Google's API infrastructure
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
            )
            return response.text.strip()
        except errors.APIError as e:
            # Catching infrastructure-specific errors (429, 503, 403, 401)
            if e.code in [429, 503] and attempt < max_retries:
                wait_time = attempt * 5
                print(f"[Warning] Google servers are busy, retrying in {wait_time}s... (attempt {attempt}/{max_retries})")
                time.sleep(wait_time)
                continue
            return f"GOOGLE_API_ERROR: {e.code} - {e.message}"
        except Exception as e:
            return f"UNEXPECTED_ERROR: {str(e)}"


def send_notification(message):
    """Sends a native desktop notification to the user."""
    try:
        clean_message = message.replace("DANGER:", "").strip()
        safe_message = clean_message[:60] + "..." if len(clean_message) > 60 else clean_message
        notification.notify(
            title="⚠️ AI Agent System Warning",
            message=safe_message,
            app_name="AI System Monitor",
            timeout=8
        )
    except Exception as e:
        print(f"Notification error: {e}")


def main():
    print("\n=== Independent AI System Monitor Started ===")
    print("Testing connection...\n")

    while True:
        hardware_data = get_system_status()
        active_processes = get_top_resource_hogs()

        ai_analysis = run_ai_analysis(hardware_data, active_processes)

        print(f"[Gemini Report] -> {ai_analysis}")

        if ai_analysis.upper().startswith("DANGER"):
            send_notification(ai_analysis)

        print("-" * 50)
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
