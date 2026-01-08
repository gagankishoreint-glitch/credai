from app.services.policy_engine import policy_engine

def test_direct():
    data = {
        "credit_score": 500,
        "annual_income": 50000,
        "total_debt": 10000,
        "monthly_debt_obligations": 500
    }
    
    passed, msg = policy_engine.check_safety(data)
    print(f"Passed: {passed}")
    print(f"Message: {msg}")
    
    if not passed and "Knockout" in msg:
        print("DIRECT TEST SUCCESS")
    else:
        print("DIRECT TEST FAILURE")

if __name__ == "__main__":
    test_direct()
