from app.db.session import SessionLocal
from app.db.models import AuditLog
from sqlalchemy import text

def test_db():
    db = SessionLocal()
    try:
        # Check connection
        res = db.execute(text("SELECT 1"))
        print(f"Connection Test: {res.fetchone()}")
        
        # Check table
        print("Checking AuditLog table...")
        logs = db.query(AuditLog).all()
        print(f"Found {len(logs)} audit logs.")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
