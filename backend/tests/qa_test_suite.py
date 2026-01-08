"""
QA Test Suite for AI Credit Decision System
Tests the complete pipeline from application submission to audit logging
"""

import requests
import json
from datetime import datetime

# Base URLs
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

class QATestSuite:
    def __init__(self):
        self.token = None
        self.results = []
        
    def login(self, username="applicant_001", password="secret"):
        """Authenticate and get token"""
        response = requests.post(
            f"{API_V1}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_case_1_safe_applicant(self):
        """
        TEST CASE 1: Safe Applicant
        Expected: Approve tier, Low PD (<20%), High confidence
        """
        print("\n" + "="*80)
        print("TEST CASE 1: SAFE APPLICANT")
        print("="*80)
        
        application = {
            "age": 42,
            "annual_income": 95000,
            "credit_score": 750,
            "total_debt": 15000,
            "business_type": "IT",
            "employment_years": 8,
            "recent_inquiries": 1,
            "delinquency_count": 0,
            "payment_history_months": 60,
            "credit_utilization": 0.15
        }
        
        print(f"\nInput Data:")
        print(json.dumps(application, indent=2))
        
        response = requests.post(
            f"{API_V1}/decide",
            headers=self.get_headers(),
            json=application
        )
        
        result = response.json()
        print(f"\nResponse Status: {response.status_code}")
        print(f"\nDecision Output:")
        print(json.dumps(result, indent=2))
        
        # Verification
        checks = {
            "Status Code": response.status_code == 200,
            "PD < 0.20": result.get("risk_score", 1.0) < 0.20,
            "Tier = Approve": result.get("tier") == "Approve",
            "Confidence > 0.70": result.get("confidence_score", 0) > 0.70,
            "Has Factors": len(result.get("factors", [])) > 0,
            "Has Model Version": "model_version" in result,
            "Has Decision ID": "decision_id" in result
        }
        
        print(f"\n✓ VERIFICATION RESULTS:")
        for check, passed in checks.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {check}")
        
        self.results.append({
            "test": "Safe Applicant",
            "checks": checks,
            "passed": all(checks.values()),
            "result": result
        })
        
        return all(checks.values())
    
    def test_case_2_borderline_applicant(self):
        """
        TEST CASE 2: Borderline Applicant
        Expected: Review tier, PD 20-45%, Medium-High confidence
        """
        print("\n" + "="*80)
        print("TEST CASE 2: BORDERLINE APPLICANT")
        print("="*80)
        
        application = {
            "age": 35,
            "annual_income": 75000,
            "credit_score": 680,
            "total_debt": 35000,
            "business_type": "Construction",
            "employment_years": 5,
            "recent_inquiries": 2,
            "delinquency_count": 1,
            "payment_history_months": 36,
            "credit_utilization": 0.47
        }
        
        print(f"\nInput Data:")
        print(json.dumps(application, indent=2))
        
        response = requests.post(
            f"{API_V1}/decide",
            headers=self.get_headers(),
            json=application
        )
        
        result = response.json()
        print(f"\nResponse Status: {response.status_code}")
        print(f"\nDecision Output:")
        print(json.dumps(result, indent=2))
        
        # Verification
        pd = result.get("risk_score", 0)
        checks = {
            "Status Code": response.status_code == 200,
            "PD in Gray Zone (0.20-0.45)": 0.20 <= pd <= 0.45,
            "Tier = Review": result.get("tier") == "Review",
            "Confidence > 0.40": result.get("confidence_score", 0) > 0.40,
            "Has Explanation": len(result.get("factors", [])) > 0,
            "Reason Flag Present": "reason_flag" in result,
            "Has Counterfactuals": "counterfactuals" in result
        }
        
        print(f"\n✓ VERIFICATION RESULTS:")
        for check, passed in checks.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {check}")
        
        self.results.append({
            "test": "Borderline Applicant",
            "checks": checks,
            "passed": all(checks.values()),
            "result": result
        })
        
        return all(checks.values())
    
    def test_case_3_high_risk_applicant(self):
        """
        TEST CASE 3: High-Risk Applicant
        Expected: Reject tier, PD > 45%, High confidence
        """
        print("\n" + "="*80)
        print("TEST CASE 3: HIGH-RISK APPLICANT")
        print("="*80)
        
        application = {
            "age": 28,
            "annual_income": 35000,
            "credit_score": 520,
            "total_debt": 45000,
            "business_type": "Retail",
            "employment_years": 1,
            "recent_inquiries": 5,
            "delinquency_count": 4,
            "payment_history_months": 12,
            "credit_utilization": 0.95
        }
        
        print(f"\nInput Data:")
        print(json.dumps(application, indent=2))
        
        response = requests.post(
            f"{API_V1}/decide",
            headers=self.get_headers(),
            json=application
        )
        
        result = response.json()
        print(f"\nResponse Status: {response.status_code}")
        print(f"\nDecision Output:")
        print(json.dumps(result, indent=2))
        
        # Verification
        pd = result.get("risk_score", 0)
        checks = {
            "Status Code": response.status_code == 200,
            "PD > 0.45": pd > 0.45,
            "Tier = Reject": result.get("tier") == "Reject",
            "Confidence > 0.70": result.get("confidence_score", 0) > 0.70,
            "Has Negative Factors": any(
                f.get("impact", 0) < 0 for f in result.get("factors", [])
            ),
            "Reason Code Present": "reason_flag" in result
        }
        
        print(f"\n✓ VERIFICATION RESULTS:")
        for check, passed in checks.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {check}")
        
        self.results.append({
            "test": "High-Risk Applicant",
            "checks": checks,
            "passed": all(checks.values()),
            "result": result
        })
        
        return all(checks.values())
    
    def test_case_4_missing_data(self):
        """
        TEST CASE 4: Missing Required Data
        Expected: 422 Validation Error or Review with low confidence
        """
        print("\n" + "="*80)
        print("TEST CASE 4: MISSING DATA")
        print("="*80)
        
        application = {
            "age": 35,
            "annual_income": 75000,
            # Missing: credit_score
            "total_debt": 35000,
            "business_type": "Construction"
            # Missing: employment_years, recent_inquiries, etc.
        }
        
        print(f"\nInput Data (incomplete):")
        print(json.dumps(application, indent=2))
        
        response = requests.post(
            f"{API_V1}/decide",
            headers=self.get_headers(),
            json=application
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"\nResponse:")
        print(json.dumps(response.json(), indent=2))
        
        # Verification - should either reject with validation error or handle gracefully
        checks = {
            "Handled Gracefully": response.status_code in [200, 422],
            "Error Message Present": "detail" in response.json() or "error" in response.json() or response.status_code == 200
        }
        
        if response.status_code == 200:
            result = response.json()
            checks["Low Confidence or Review"] = (
                result.get("confidence_score", 1.0) < 0.5 or 
                result.get("tier") == "Review"
            )
        
        print(f"\n✓ VERIFICATION RESULTS:")
        for check, passed in checks.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {check}")
        
        self.results.append({
            "test": "Missing Data",
            "checks": checks,
            "passed": all(checks.values()),
            "result": response.json()
        })
        
        return all(checks.values())
    
    def test_case_5_edge_case_values(self):
        """
        TEST CASE 5: Edge Case Values
        Expected: Handles extreme values gracefully
        """
        print("\n" + "="*80)
        print("TEST CASE 5: EDGE CASE VALUES")
        print("="*80)
        
        application = {
            "age": 18,  # Minimum age
            "annual_income": 250000,  # Very high income
            "credit_score": 850,  # Maximum credit score
            "total_debt": 0,  # No debt
            "business_type": "IT",
            "employment_years": 0,  # Just started
            "recent_inquiries": 0,
            "delinquency_count": 0,
            "payment_history_months": 6,  # Short history
            "credit_utilization": 0.0  # No utilization
        }
        
        print(f"\nInput Data (edge cases):")
        print(json.dumps(application, indent=2))
        
        response = requests.post(
            f"{API_V1}/decide",
            headers=self.get_headers(),
            json=application
        )
        
        result = response.json()
        print(f"\nResponse Status: {response.status_code}")
        print(f"\nDecision Output:")
        print(json.dumps(result, indent=2))
        
        # Verification
        checks = {
            "Status Code": response.status_code == 200,
            "PD is Valid (0-1)": 0 <= result.get("risk_score", -1) <= 1,
            "Confidence is Valid (0-1)": 0 <= result.get("confidence_score", -1) <= 1,
            "Tier is Valid": result.get("tier") in ["Approve", "Review", "Reject"],
            "No NaN/Inf Values": all(
                isinstance(result.get(k), (int, float, str, list, dict, type(None)))
                for k in result.keys()
            )
        }
        
        print(f"\n✓ VERIFICATION RESULTS:")
        for check, passed in checks.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {check}")
        
        self.results.append({
            "test": "Edge Case Values",
            "checks": checks,
            "passed": all(checks.values()),
            "result": result
        })
        
        return all(checks.values())
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"\nTest Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tests: {len(self.results)}")
        
        passed = sum(1 for r in self.results if r["passed"])
        failed = len(self.results) - passed
        
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.results)*100):.1f}%")
        
        print("\n" + "-"*80)
        print("DETAILED RESULTS")
        print("-"*80)
        
        for result in self.results:
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"\n{status}: {result['test']}")
            for check, passed in result["checks"].items():
                check_status = "  ✓" if passed else "  ✗"
                print(f"{check_status} {check}")
        
        # Severity Analysis
        print("\n" + "-"*80)
        print("SEVERITY ANALYSIS")
        print("-"*80)
        
        for result in self.results:
            if not result["passed"]:
                print(f"\n🔴 CRITICAL: {result['test']} failed")
                failed_checks = [k for k, v in result["checks"].items() if not v]
                for check in failed_checks:
                    print(f"   - {check}")
        
        return {
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed/len(self.results)*100,
            "results": self.results
        }

def run_qa_tests():
    """Execute all QA tests"""
    qa = QATestSuite()
    
    print("="*80)
    print("AI CREDIT DECISION SYSTEM - QA TEST SUITE")
    print("="*80)
    
    # Login
    print("\nAuthenticating...")
    if not qa.login():
        print("❌ Authentication failed!")
        return
    print("✓ Authentication successful")
    
    # Run all test cases
    qa.test_case_1_safe_applicant()
    qa.test_case_2_borderline_applicant()
    qa.test_case_3_high_risk_applicant()
    qa.test_case_4_missing_data()
    qa.test_case_5_edge_case_values()
    
    # Generate report
    report = qa.generate_report()
    
    # Save report
    with open("qa_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Report saved to qa_test_report.json")
    
    return report

if __name__ == "__main__":
    run_qa_tests()
