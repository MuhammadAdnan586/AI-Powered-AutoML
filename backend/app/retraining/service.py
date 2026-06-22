"""
Retraining Service
Handles cron schedule management and actual model retraining logic.
"""

import time
import joblib
import pandas as pd
from datetime import datetime
from typing import List, Optional
from croniter import croniter
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.retraining.models import RetrainingSchedule, RetrainingLog, RetrainingStatus
from app.retraining.schemas import ScheduleCreate
from app.notifications.service import NotificationService


class RetrainingService:
    def __init__(self, db: Session):
        self.db = db

    def _next_run(self, cron_expr: str) -> datetime:
        cron = croniter(cron_expr, datetime.utcnow())
        return cron.get_next(datetime)

    def create_schedule(self, payload: ScheduleCreate, user_id: int) -> RetrainingSchedule:
        if not croniter.is_valid(payload.cron_expression):
            raise HTTPException(status_code=400, detail="Invalid cron expression")

        schedule = RetrainingSchedule(
            user_id=user_id,
            model_id=payload.model_id,
            dataset_id=payload.dataset_id,
            cron_expression=payload.cron_expression,
            next_run_at=self._next_run(payload.cron_expression),
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def list_schedules(self, user_id: int) -> List[RetrainingSchedule]:
        return self.db.query(RetrainingSchedule).filter_by(user_id=user_id).all()

    def toggle(self, schedule_id: int, user_id: int) -> RetrainingSchedule:
        sched = self.db.query(RetrainingSchedule).filter_by(
            id=schedule_id, user_id=user_id
        ).first()
        if not sched:
            raise HTTPException(status_code=404, detail="Schedule not found")
        sched.is_active = not sched.is_active
        self.db.commit()
        return sched

    def delete_schedule(self, schedule_id: int, user_id: int) -> None:
        sched = self.db.query(RetrainingSchedule).filter_by(
            id=schedule_id, user_id=user_id
        ).first()
        if not sched:
            raise HTTPException(status_code=404, detail="Schedule not found")
        self.db.delete(sched)
        self.db.commit()

    def get_logs(self, schedule_id: int, user_id: int) -> List[RetrainingLog]:
        sched = self.db.query(RetrainingSchedule).filter_by(
            id=schedule_id, user_id=user_id
        ).first()
        if not sched:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return (
            self.db.query(RetrainingLog)
            .filter_by(schedule_id=schedule_id)
            .order_by(RetrainingLog.triggered_at.desc())
            .all()
        )

    # ── Core retraining logic ─────────────────────────────────────────────────

    def run_retraining(self, schedule_id: int, user_id: int) -> None:
        """
        Run the retraining job:
        1. Load existing model + dataset
        2. Retrain with latest data
        3. Compare accuracy before/after
        4. Save new model version
        5. Notify user
        """
        from app.model_registry.registry import ModelRegistry
        from app.datasets.models import Dataset

        sched = self.db.query(RetrainingSchedule).filter_by(
            id=schedule_id, user_id=user_id
        ).first()
        if not sched:
            return

        sched.last_status = RetrainingStatus.RUNNING
        self.db.commit()

        log = RetrainingLog(
            schedule_id=schedule_id,
            status=RetrainingStatus.RUNNING,
            triggered_at=datetime.utcnow(),
        )
        self.db.add(log)
        self.db.commit()

        start_time = time.time()
        try:
            # Load model
            model_record: ModelRegistry = sched.model
            model = joblib.load(model_record.artifact_path)

            # Load dataset
            dataset: Dataset = sched.dataset
            df = pd.read_csv(dataset.file_path)
            target_col = model_record.target_column

            X = df.drop(columns=[target_col])
            y = df[target_col]

            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Accuracy before retraining
            acc_before = accuracy_score(y_test, model.predict(X_test))

            # Retrain
            model.fit(X_train, y_train)
            acc_after = accuracy_score(y_test, model.predict(X_test))

            # Save new model
            new_path = model_record.artifact_path.replace(".pkl", f"_retrained_{int(time.time())}.pkl")
            joblib.dump(model, new_path)

            # Update registry
            model_record.artifact_path = new_path
            model_record.accuracy = str(round(acc_after * 100, 2))
            model_record.version = str(float(model_record.version or "1.0") + 0.1)
            self.db.commit()

            duration = int(time.time() - start_time)
            log.status = RetrainingStatus.SUCCESS
            log.accuracy_before = f"{round(acc_before * 100, 2)}%"
            log.accuracy_after = f"{round(acc_after * 100, 2)}%"
            log.duration_seconds = duration

            sched.last_status = RetrainingStatus.SUCCESS
            sched.last_run_at = datetime.utcnow()
            sched.next_run_at = self._next_run(sched.cron_expression)
            self.db.commit()

            # Notify user
            notif_service = NotificationService(self.db)
            notif_service.send(
                user_id=user_id,
                title="Model Retraining Complete ✅",
                message=(
                    f"Model '{model_record.model_name}' retrained successfully.\n"
                    f"Accuracy: {log.accuracy_before} → {log.accuracy_after}"
                ),
                notification_type="retraining",
            )

        except Exception as e:
            log.status = RetrainingStatus.FAILED
            log.error_message = str(e)
            sched.last_status = RetrainingStatus.FAILED
            self.db.commit()

            notif_service = NotificationService(self.db)
            notif_service.send(
                user_id=user_id,
                title="Retraining Failed ❌",
                message=f"Retraining job failed: {str(e)}",
                notification_type="retraining",
            )
