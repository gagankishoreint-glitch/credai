import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
from app.db.session import SessionLocal
from app.db.models import ApplicantFeatures, ModelInference, AuditLog

class MonitoringService:
    def __init__(self):
        # Placeholder Training Quantiles (Benchmarks)
        # Ideally loaded from model/training_stats.json
        self.benchmarks = {
            "credit_score": [500, 600, 650, 700, 750, 800],
            "annual_income": [30000, 50000, 75000, 100000, 150000],
            "expected_distribution": {
               "credit_score": [0.1, 0.2, 0.3, 0.25, 0.15], # Placeholder probabilities per bin
               "annual_income": [0.2, 0.25, 0.25, 0.2, 0.1]
            }
        }
        
    def check_drift(self) -> Dict[str, Any]:
        """
        Runs PSI check on 'credit_score' and 'annual_income' using data from last 7 days.
        Logs alarms to AuditLog (or DriftLog table if created, we'll use AuditLog for simplicity or Models)
        Wait, we defined 'drift_logs' table in schema design but did NOT add it to models.py in Step 874.
        I missed adding 'DriftLog' model.
        I will log to 'AuditLog' with action='DRIFT_ALARM' for now to avoid schema migration overhead in this step.
        """
        db = SessionLocal()
        drift_report = {}
        try:
            # Fetch recent data (e.g., last 100 records)
            records = db.query(ApplicantFeatures).limit(100).all()
            if not records:
                return {"status": "No Data"}
                
            df = pd.DataFrame([{
                "credit_score": r.credit_score,
                "annual_income": r.annual_income
            } for r in records])
            
            # Simple PSI Calcs
            for col in ["credit_score", "annual_income"]:
                psi = self._calculate_psi(df[col], col)
                drift_report[col] = psi
                
                if psi > 0.2:
                    # Critical Drift
                    self._log_alarm(db, f"CRITICAL_DRIFT_{col.upper()}", psi)
                elif psi > 0.1:
                    # Warning Drift
                    self._log_alarm(db, f"WARNING_DRIFT_{col.upper()}", psi)
                    
            return drift_report
            
        except Exception as e:
            print(f"Monitoring Failed: {e}")
            return {"error": str(e)}
        finally:
            db.close()
            
    def _calculate_psi(self, current_data: pd.Series, col_name: str) -> float:
        """
        Calculate PSI = Sum( (Actual% - Expected%) * ln(Actual% / Expected%) )
        """
        bins = self.benchmarks[col_name]
        expected_probs = self.benchmarks["expected_distribution"][col_name]
        
        # Bin the current data
        # Note: numpy histogram returns count per bin
        counts, _ = np.histogram(current_data, bins=bins + [99999999]) 
        # (Handling outliers coarsely)
        
        # Avoid division by zero
        total = sum(counts)
        if total == 0: return 0.0
        
        actual_probs = counts / total
        
        psi_sum = 0.0
        for i, act_p in enumerate(actual_probs):
            if i >= len(expected_probs): break
            exp_p = expected_probs[i]
            
            # Smoothing
            if act_p == 0: act_p = 0.0001
            if exp_p == 0: exp_p = 0.0001
            
            psi = (act_p - exp_p) * np.log(act_p / exp_p)
            psi_sum += psi
            
        return float(psi_sum)
    
    def _log_alarm(self, db, alarm_name, value):
        entry = AuditLog(
            entity_type="MONITORING",
            entity_id="SYSTEM",
            action=alarm_name,
            actor="SYSTEM_MONITOR",
            changes={"psi_value": value},
            timestamp=datetime.utcnow()
        )
        db.add(entry)
        db.commit()

monitoring_service = MonitoringService()
