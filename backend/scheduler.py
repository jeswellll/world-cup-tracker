from apscheduler.schedulers.background import BackgroundScheduler
from sync_live_data import sync_matches_from_api
import database, models
import datetime

scheduler = BackgroundScheduler()

def dynamic_sync_job():
    """Checks if we are in an active match window and syncs accordingly."""
    # A simple way to handle dynamic polling:
    # This job runs every 2 minutes. We check if there are matches "IN_PLAY" (or today).
    # If not, we only run the sync if the last sync was >= 10 mins ago.
    
    # Check if there are any matches in play right now
    db = next(database.get_db())
    try:
        active_matches = db.query(models.Match).filter(models.Match.status == "In Progress").count()
    except Exception as e:
        db.close()
        return
        
    now = datetime.datetime.utcnow()
    
    if not hasattr(dynamic_sync_job, "last_run"):
        dynamic_sync_job.last_run = None

    is_active_window = active_matches > 0
    
    # If active window, we sync.
    # If not active window, we sync only if 10 mins have passed since last sync.
    if is_active_window or dynamic_sync_job.last_run is None or (now - dynamic_sync_job.last_run).total_seconds() >= 600:
        print(f"[{now}] Running sync job. Active Window: {is_active_window}")
        sync_matches_from_api(db)
        db.commit()
        dynamic_sync_job.last_run = now
    else:
        print(f"[{now}] Skipping sync job (non-active window).")
        
    db.close()

def start_scheduler():
    scheduler.add_job(dynamic_sync_job, 'interval', minutes=2)
    scheduler.start()
    
def stop_scheduler():
    scheduler.shutdown()
