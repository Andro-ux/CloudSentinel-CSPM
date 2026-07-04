from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def trigger_scheduled_scan():
    logger.info("Scheduler: Enqueuing scan of all active accounts to Celery...")
    try:
        from backend.celery_worker import run_scan_task
        run_scan_task.delay(None)  # None = scan every non-disabled Account
    except Exception as e:
        logger.error(f"Scheduler failed to enqueue scan task: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(trigger_scheduled_scan, 'interval', minutes=5, id='run_scan_job', replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started. Scan tasks will be enqueued to Celery every 5 minutes.")

