from sqlalchemy.orm import Session
from . import models

def create_alert(db: Session, alert_data):
    a = models.Alert(
        type=alert_data.get("type"),
        location=alert_data.get("location"),
        priority=alert_data.get("priority"),
        details=alert_data.get("details"),
        status=alert_data.get("status", "Active")
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a

def list_alerts(db: Session, limit: int = 100):
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(limit).all()