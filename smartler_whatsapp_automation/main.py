from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
from pytz import timezone
from dotenv import load_dotenv
import os
import threading

from manager import execute_task

app = FastAPI(title="FastAPI with Scheduler")

# Load env
load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

# Initialize scheduler
tz = timezone("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=tz)

# Lock for graceful shutdown
task_lock = threading.Lock()


def safe_execute_task():
    """Ensure the task runs safely and completes before shutdown."""
    with task_lock:
        print("Task started...")
        try:
            execute_task()
        finally:
            print("Task finished.")


@app.on_event("startup")
def start_scheduler():
    # Run every 5 minutes using cron expression
    scheduler.add_job(
        safe_execute_task,
        CronTrigger.from_crontab("*/5 * * * *", timezone=tz),
        id="my_task",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started")

    # Graceful shutdown
    def shutdown_scheduler():
        print("Shutting down scheduler...")
        # Wait until any running task finishes
        with task_lock:
            print("No running task. Scheduler shutting down.")
        scheduler.shutdown()

    atexit.register(shutdown_scheduler)


@app.get("/")
def read_root():
    return {"message": "FastAPI with Scheduler is running!"}

