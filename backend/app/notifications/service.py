"""
Notification Service
Handles in-app notifications (DB) + email notifications (SMTP).
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from sqlalchemy.orm import Session

from app.notifications.models import Notification
from app.users.models import User
from app.config.settings import settings


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def send(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "general",
        send_email: bool = True,
    ) -> Notification:
        """
        Create in-app notification + optionally send email.
        """
        # 1. In-app notification
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)

        # 2. Email notification
        if send_email and settings.SMTP_HOST:
            try:
                user = self.db.query(User).filter_by(id=user_id).first()
                if user and user.email:
                    self._send_email(
                        to_email=user.email,
                        subject=title,
                        body=message,
                    )
            except Exception as e:
                # Email failure should not break the main flow
                print(f"[Notification] Email send failed: {e}")

        return notif

    def _send_email(self, to_email: str, subject: str, body: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email

        # Plain text fallback + HTML version
        text_part = MIMEText(body, "plain")
        html_body = f"""
        <html><body>
          <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;">
            <h2 style="color:#2563eb;">{subject}</h2>
            <p style="white-space:pre-line;">{body}</p>
            <hr/>
            <small>AutoML SaaS Platform</small>
          </div>
        </body></html>
        """
        html_part = MIMEText(html_body, "html")
        msg.attach(text_part)
        msg.attach(html_part)

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())

    # ── Query helpers ─────────────────────────────────────────────────────────

    def get_notifications(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        q = self.db.query(Notification).filter_by(user_id=user_id)
        if unread_only:
            q = q.filter_by(is_read=False)
        return q.order_by(Notification.created_at.desc()).all()

    def mark_read(self, notification_id: int, user_id: int) -> None:
        notif = self.db.query(Notification).filter_by(
            id=notification_id, user_id=user_id
        ).first()
        if notif:
            notif.is_read = True
            self.db.commit()

    def mark_all_read(self, user_id: int) -> int:
        count = (
            self.db.query(Notification)
            .filter_by(user_id=user_id, is_read=False)
            .update({"is_read": True})
        )
        self.db.commit()
        return count

    def delete_notification(self, notification_id: int, user_id: int) -> None:
        self.db.query(Notification).filter_by(
            id=notification_id, user_id=user_id
        ).delete()
        self.db.commit()
