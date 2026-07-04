import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "cloudsentinel_tasks",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True
)

@celery_app.task(name="cloudsentinel_tasks.run_scan_task")
def run_scan_task(account_id: int = None):
    from backend.rules.engine import run_scan, run_scan_all_accounts
    try:
        if account_id is not None:
            print(f"Celery Worker: Triggering scan for account {account_id}...")
            run_scan(account_id)
        else:
            print("Celery Worker: Triggering scan for all accounts...")
            run_scan_all_accounts()
        print("Celery Worker: Security scan(s) completed.")
        return "SUCCESS"
    except Exception as e:
        print(f"Celery Worker: Security scan failed: {e}")
        return f"FAILED: {e}"
