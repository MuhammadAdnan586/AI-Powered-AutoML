"""
Module 4 - Background Scheduler
Uses APScheduler to run cron-based retraining jobs.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
import logging
from app.database.session import SessionLocal

logger = logging.getLogger("scheduler")

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        # Memory jobstore — no DB connection needed for scheduler itself
        _scheduler = AsyncIOScheduler(
            jobstores={"default": {"type": "memory"}},
            timezone="UTC"
        )
    return _scheduler


async def _run_retraining_job(schedule_id: int, user_id: int):
    from app.retraining.service import RetrainingService
    db: Session = SessionLocal()
    try:
        service = RetrainingService(db)
        service.run_retraining(schedule_id, user_id)
        logger.info(f"Retraining job completed for schedule_id={schedule_id}")
    except Exception as e:
        logger.error(f"Retraining job failed for schedule_id={schedule_id}: {e}")
    finally:
        db.close()


def add_retraining_job(schedule_id: int, user_id: int, cron_expression: str):
    scheduler = get_scheduler()
    job_id = f"retrain_{schedule_id}"
    parts = cron_expression.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_expression}")
    minute, hour, day, month, day_of_week = parts
    scheduler.add_job(
        _run_retraining_job,
        CronTrigger(
            minute=minute, hour=hour, day=day,
            month=month, day_of_week=day_of_week,
        ),
        id=job_id,
        args=[schedule_id, user_id],
        replace_existing=True,
        misfire_grace_time=3600,
    )
    logger.info(f"Registered retraining job: {job_id}")


def remove_retraining_job(schedule_id: int):
    scheduler = get_scheduler()
    job_id = f"retrain_{schedule_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Removed retraining job: {job_id}")


def sync_jobs_from_db():
    from app.retraining.models import RetrainingSchedule, RetrainingLog  # noqa
    from app.auth.models import User  # noqa
    from app.datasets.models import Dataset  # noqa
    from app.notifications.models import Notification  # noqa

    db: Session = SessionLocal()
    try:
        schedules = db.query(RetrainingSchedule).filter_by(is_active=True).all()
        for sched in schedules:
            add_retraining_job(sched.id, sched.user_id, sched.cron_expression)
        logger.info(f"Synced {len(schedules)} retraining jobs from database")
    except Exception as e:
        logger.warning(f"Could not sync jobs from DB (first run is normal): {e}")
    finally:
        db.close()


async def start_scheduler():
    scheduler = get_scheduler()
    sync_jobs_from_db()
    scheduler.start()
    logger.info("APScheduler started")


async def stop_scheduler():
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")