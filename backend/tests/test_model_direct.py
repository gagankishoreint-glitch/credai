"""
Minimal test - directly call model service
"""
import sys
sys.path.insert(0, 'k:/credit-ai-model/backend')

from app.services.model_service import model_service

# Test data
data = {
    "age": 42,
    "annual_income": 95000,
    "credit_score": 750,
    "total_debt": 15000,
    "business_type": "IT",
    "monthly_debt_obligations": 1250
}

print("Testing model service directly...")
print(f"Input: {data}\n")

try:
    result = model_service.predict_probability(data)
    print("✓ Model service works!")
    print(f"Result: {result}")
except Exception as e:
    print(f"✗ Model service failed: {e}")
    import traceback
    traceback.print_exc()
