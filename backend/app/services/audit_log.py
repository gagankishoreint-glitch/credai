from datetime import datetime
from app.db.session import SessionLocal
from app.db.models import AuditLog

class AuditService:
    def log_event(self, event_type: str, data: dict):
        db = SessionLocal()
        try:
            entry = AuditLog(
                entity_type="SYSTEM", # Should be passed dynamically ideally
                entity_id=data.get("app_id", "UNKNOWN"),
                action=event_type,
                actor="SYSTEM",
                changes=data,
                timestamp=datetime.utcnow()
            )
            db.add(entry)
            db.commit()
        except Exception as e:
            print(f"Audit Log Failed: {e}")
            db.rollback()
        finally:
            db.close()

audit_service = AuditService()
