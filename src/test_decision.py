from decision import credit_decision

sample_applicant = {
    "business_type": "Manufacturing",
    "years_in_operation": 10,
    "annual_revenue": 6000000,
    "monthly_cashflow": 500000,
    "loan_amount_requested": 1200000,
    "credit_score": 720,
    "existing_loans": 1,
    "debt_to_income_ratio": 0.25,
    "collateral_value": 2500000,
    "repayment_history": "Good"
}

result = credit_decision(sample_applicant)
print(result)
