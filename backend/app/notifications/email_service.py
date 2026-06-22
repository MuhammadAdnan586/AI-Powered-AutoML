from datetime import datetime
from app.database.db import db
from .models import Notification
from .email_service import send_training_complete_email, send_retraining_email

def create_notification(user_id, title, message, notif_type='info'):
    """In-app notification create karo"""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notif_type=notif_type
    )
    db.session.add(notif)
    db.session.commit()
    return notif.to_dict()

def notify_training_complete(user_id, user_email, model_name, accuracy, project_name):
    """Training complete - email + in-app notification"""
    
    # In-app notification
    create_notification(
        user_id=user_id,
        title=f"✅ Model Ready: {model_name}",
        message=f"Your model '{model_name}' training is complete! Accuracy: {accuracy}%",
        notif_type='success'
    )
    
    # Email notification
    if user_email:
        send_training_complete_email(user_email, model_name, accuracy, project_name)
    
    return {'notified': True}

def get_user_notifications(user_id, unread_only=False):
    """User ki notifications"""
    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    notifications = query.order_by(Notification.created_at.desc()).limit(50).all()
    return [n.to_dict() for n in notifications]

def mark_as_read(notif_id, user_id):
    """Notification read mark karo"""
    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
        return {'success': True}
    return {'error': 'Not found'}