import schedule
import time
import subprocess

LOG_FILE = "/var/log/whatsapp_manager.log"

def run_manager():
    with open(LOG_FILE, "a") as log_file:
        subprocess.run(
            ["uv", "run", "/usr/local/smartler_whatsapp_automation/manager.py"],
            stdout=log_file,
            stderr=log_file,
            text=True
        )

# run every 1 minute
schedule.every().minute.do(run_manager)

while True:
    schedule.run_pending()
    time.sleep(1)

