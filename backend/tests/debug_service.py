import sys
import os
# Add root to sys.path to mimic module execution
sys.path.append(os.getcwd())

from app.services.policy_engine import policy_engine

def test_policy():
    print("\nTesting Policy Engine...")
    # Case 1: Clear Approve
    t, c, f = policy_engine.apply_decision_logic(0.10)
    print(f"PD=0.10 -> {t}, Conf={c:.2f}, Flag={f}")
    
    # Case 2: Deep Gray (0.325 is mid of 0.20-0.45)
    t, c, f = policy_engine.apply_decision_logic(0.325)
    print(f"PD=0.325 -> {t}, Conf={c:.2f}, Flag={f}")
    
    # Case 3: Construction Mitigation (0.50 should be Review, normally Reject)
    t, c, f = policy_engine.apply_decision_logic(0.50, business_type="Construction")
    print(f"PD=0.50 (Const) -> {t}, Conf={c:.2f}, Flag={f}")

if __name__ == "__main__":
    # test_direct()
    test_policy()
