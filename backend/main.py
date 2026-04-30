from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import models, crud

Base.metadata.create_all(bind=engine)
app = FastAPI(title="I4C Backend Alerts")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/alerts")
def create_alert(alert: dict, db: Session = Depends(get_db)):
    a = crud.create_alert(db, alert)
    return {"id": a.id, "status": "created"}

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    res = crud.list_alerts(db)
    return [{"id": r.id, "type": r.type, "location": r.location, "priority": r.priority, "details": r.details, "status": r.status, "created_at": r.created_at} for r in res]