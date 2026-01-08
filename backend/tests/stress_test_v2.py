import requests
import random
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Configuration
API_URL = "http://localhost:8000/api/v1/decisions/assess"
NUM_REQUESTS = 100
CONCURRENCY = 10

def generate_synthetic_applicant():
    """
    Generates a random applicant profile, including 'Adversarial' profiles
    designed to trick the model (e.g. High Income but Terrible Credit).
    """
    profile_type = random.choice(['standard', 'risky', 'adversarial_wealthy_defaulter'])
    
    if profile_type == 'standard':
        return {
            "applicant_id": f"SYN-{random.randint(10000,99999)}",
            "annual_income": random.uniform(30000, 120000),
            "credit_score": random.randint(580, 820),
            "total_debt": random.uniform(0, 50000),
            "loan_amount": random.uniform(5000, 30000),
            "business_type": random.choice(["Retail", "IT", "Other"])
        }
    elif profile_type == 'risky':
        return {
            "applicant_id": f"RISK-{random.randint(10000,99999)}",
            "annual_income": random.uniform(20000, 45000),
            "credit_score": random.randint(300, 600),
            "total_debt": random.uniform(20000, 80000),
            "loan_amount": random.uniform(10000, 50000),
            "business_type": "Retail"
        }
    elif profile_type == 'adversarial_wealthy_defaulter':
        # High Income, but terrible credit history. 
        # Goal: See if Income biases the model to approve.
        return {
            "applicant_id": f"ADV-{random.randint(10000,99999)}",
            "annual_income": random.uniform(150000, 300000), # Very High Income
            "credit_score": random.randint(400, 550),        # Very Low Score
            "total_debt": random.uniform(100000, 200000),    # High Debt
            "loan_amount": random.uniform(5000, 20000),      # Small Loan (should be enticing)
            "business_type": "Real Estate"
        }

def send_request(applicant):
    try:
        start_time = time.time()
        # Mapping frontend fields to API schema if needed
        # Assuming API accepts flat JSON or specific schema. 
        # Adjusting to likely API schema based on usage.
        payload = {
            "applicant_id": applicant["applicant_id"],
            "income": applicant["annual_income"], # Note field name might be income/annual_income
            "credit_score": applicant["credit_score"],
            "total_debt": applicant["total_debt"],
            "business_type": applicant["business_type"]
        }
        
        response = requests.post(API_URL, json=payload)
        latency = (time.time() - start_time) * 1000
        
        result = {
            "status": response.status_code,
            "latency_ms": latency,
            "profile_type": "adversarial" if "ADV" in applicant["applicant_id"] else "standard",
            "decision": "UNKNOWN"
        }
        
        if response.status_code == 200:
            data = response.json()
            result["decision"] = data.get("decision", "UNKNOWN")
            result["model_score"] = data.get("score", 0)
        
        return result
        
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

def run_stress_test():
    print(f"🚀 Starting Adversarial Stress Test ({NUM_REQUESTS} requests)...")
    
    applicants = [generate_synthetic_applicant() for _ in range(NUM_REQUESTS)]
    results = []
    
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        for res in executor.map(send_request, applicants):
            results.append(res)
            
    # Analysis
    df = pd.DataFrame(results)
    print("\n📊 Test Results Summary:")
    print(f"Total Requests: {len(df)}")
    print(f"Success Rate: {len(df[df['status'] == 200]) / len(df) * 100:.1f}%")
    print(f"Avg Latency: {df['latency_ms'].mean():.2f}ms")
    
    # Adversarial Check
    adv_df = df[df['profile_type'] == 'adversarial']
    if not adv_df.empty:
        # Check if any adversarial (High Income / Low Score) got Approved
        # Assuming 'APPROVE' or 'Tier 1' is approval
        failures = adv_df[adv_df['decision'].astype(str).str.contains("APPROVE", case=False)]
        
        print("\n🛡️ Security Analysis (Adversarial Profiles):")
        print(f"Adversarial Profiles Tested: {len(adv_df)}")
        print(f"False Approvals (Failures): {len(failures)}")
        
        if not failures.empty:
            print("⚠️ WARNING: The model approved High-Income/Low-Credit applicants! Policy adjustment needed.")
        else:
            print("✅ SUCCESS: The model correctly rejected/reviewed all adversarial profiles.")

if __name__ == "__main__":
    run_stress_test()
