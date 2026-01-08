from app.db.session import SessionLocal
from app.db.models import AuditLog, Application, Decision, ModelInference

def validate_data_integrity():
    db = SessionLocal()
    try:
        # Check Application Count
        apps = db.query(Application).all()
        print(f"Applications: {len(apps)}")
        
        # Check Decision Count
        decs = db.query(Decision).all()
        print(f"Decisions: {len(decs)}")
        
        if len(apps) > 0:
            app = apps[-1]
            print(f"Latest App ID: {app.id}")
            print(f"  - Status: {app.status}")
            print(f"  - Features: {app.features.annual_income} (Income)")
            print(f"  - Inferences: {app.inferences[0].raw_probability}")
            print(f"  - Decision: {app.decisions[0].tier}")
            
        # Check Audit Logs
        logs = db.query(AuditLog).all()
        print(f"Audit Logs: {len(logs)}")
        for l in logs[-2:]:
            print(f"  - Log: {l.action} -> {l.entity_id}")
            
    finally:
        db.close()

if __name__ == "__main__":
    validate_data_integrity()
