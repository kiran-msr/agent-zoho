from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from pytz import timezone 


from manager import execute_task

app = FastAPI(title="FastAPI with Scheduler")

# Initialize scheduler
tz = timezone("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=tz)

@app.on_event("startup")
def start_scheduler():
    # Add job to run every 10 seconds
    scheduler.add_job(execute_task, IntervalTrigger(minutes=5, timezone=tz), id="my_task", replace_existing=True)
    scheduler.start()
    print("Scheduler started")

    # Shut down scheduler on app exit
    atexit.register(lambda: scheduler.shutdown())

@app.get("/")
def read_root():
    return {"message": "FastAPI with Scheduler is running!"}

