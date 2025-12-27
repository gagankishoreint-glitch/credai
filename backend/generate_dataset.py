import pandas as pd
import numpy as np
import random
import os
import json

def generate_dataset(num_records=5000):
    """
    Generates a rich synthetic dataset for business credit evaluation.
    Includes advanced financial metrics, promoter stats, and realistic risk factors.
    """
    
    # Set seed
    np.random.seed(42)
    random.seed(42)
    
    ids = [f'APP_{i:05d}' for i in range(1, num_records + 1)]
    
    # --- Business Profile ---
    business_types = np.random.choice(
        ['Manufacturing', 'Retail/Trading', 'Services', 'Tech/Startup', 'Logistics', 'Construction'], 
        size=num_records, 
        p=[0.2, 0.3, 0.25, 0.1, 0.1, 0.05]
    )
    
    # Years in Operation (Gamma dist, skewed to 2-8 years)
    years_in_opp = np.random.gamma(shape=2.5, scale=3.0, size=num_records).astype(int)
    years_in_opp = np.clip(years_in_opp, 0, 40)
    
    # --- Promoter Info ---
    # Promoter Credit Score (300-900, bimodally distributed somewhat)
    # Mixture of two normals: one around 650 (avg), one around 780 (good)
    score_pop1 = np.random.normal(650, 80, int(num_records * 0.6))
    score_pop2 = np.random.normal(780, 50, int(num_records * 0.4))
    credit_scores = np.concatenate([score_pop1, score_pop2])
    np.random.shuffle(credit_scores)
    credit_scores = np.clip(credit_scores.astype(int), 300, 900)
    
    promoter_exp = np.clip(years_in_opp + np.random.randint(0, 15, size=num_records), 1, 50)
    prior_default_history = np.random.choice([0, 1], size=num_records, p=[0.92, 0.08]) # 8% have prior default
    
    # --- Loan Details ---
    # Purposes
    purposes = ['Working Capital', 'Expansion', 'Equipment Purchase', 'Inventory Restocking', 'Debt Consolidation']
    loan_purpose = np.random.choice(purposes, size=num_records)
    
    # Tenure (months): 12, 24, 36, 48, 60
    loan_tenure = np.random.choice([12, 24, 36, 48, 60], size=num_records, p=[0.1, 0.2, 0.4, 0.2, 0.1])
    
    # --- Financials ---
    # Annual Revenue (Log-normal)
    annual_revenue = np.random.lognormal(mean=15.5, sigma=1.2, size=num_records) # ~5Cr avg
    annual_revenue = np.clip(annual_revenue, 500000, 500000000).astype(int)
    
    # GST Turnover (Usually 80-120% of reported revenue for honest biz, implies integrity check)
    gst_turnover = (annual_revenue * np.random.uniform(0.8, 1.2, size=num_records)).astype(int)
    
    # Margins based on Biz Type
    ebitda_margins = []
    net_margins = []
    
    margin_profiles = {
        'Manufacturing': (0.15, 0.08), # EBITDA, Net
        'Retail/Trading': (0.08, 0.03),
        'Services': (0.25, 0.15),
        'Tech/Startup': (0.10, -0.05), # Volatile
        'Logistics': (0.12, 0.05),
        'Construction': (0.14, 0.06)
    }
    
    for bt in business_types:
        base_ebitda, base_net = margin_profiles[bt]
        # Add noise
        e_mar = np.random.normal(base_ebitda, 0.05)
        n_mar = np.random.normal(base_net, 0.03)
        ebitda_margins.append(e_mar)
        net_margins.append(n_mar)
        
    ebitda_margins = np.array(ebitda_margins)
    net_margins = np.array(net_margins)
    
    current_ebitda = (annual_revenue * ebitda_margins).astype(int)
    net_profit = (annual_revenue * net_margins).astype(int)
    
    # Total Debt & obligations
    # Debt usually multiple of EBITDA (2x - 5x is risky)
    debt_to_ebitda = np.random.uniform(0.5, 6.0, size=num_records)
    total_debt = np.abs(curr_ebitda * debt_to_ebitda).astype(int) if 'curr_ebitda' in locals() else (annual_revenue * 0.3).astype(int)
    # Fix variable name reference if needed, ensuring calc uses correct array
    total_debt = np.abs(current_ebitda * debt_to_ebitda).astype(int)
    total_debt = np.maximum(total_debt, 0)

    # Existing EMI (Monthly debt obligation)
    # Roughly Total Debt / (3-7 years * 12)
    existing_emi = (total_debt / np.random.uniform(36, 84, size=num_records)).astype(int)
    
    # Requested Loan
    loan_amount = (annual_revenue * np.random.uniform(0.05, 0.4, size=num_records)).astype(int)
    loan_amount = np.clip(loan_amount, 100000, 50000000)
    
    # Proposed EMI for NEW loan (approx)
    # Rate ~12-18% p.a.
    interest_rate = np.random.uniform(0.12, 0.18, size=num_records) / 12 # Monthly
    # Simple AMI approx: (P * r) matches basic interest, amortized is complex, let's approx linear
    # EMI ~ (P + P*r*N)/N = P/N + P*r
    proposed_emi = (loan_amount / loan_tenure) + (loan_amount * interest_rate)
    
    # DSCR (Debt Service Coverage Ratio)
    # (EBITDA / (Existing EMI*12 + Proposed EMI*12))
    total_annual_obligation = (existing_emi * 12) + (proposed_emi * 12)
    # Avoid zero div
    total_annual_obligation = np.maximum(total_annual_obligation, 1)
    dscr = current_ebitda / total_annual_obligation
    
    # Collateral
    collateral_types = ['Real Estate', 'Machinery', 'Inventory', 'Receivables', 'None']
    collateral_type = []
    collateral_value = []
    
    for i in range(num_records):
        bt = business_types[i]
        la = loan_amount[i]
        
        # Determine likely collateral
        if bt == 'Manufacturing':
            ctype = np.random.choice(['Machinery', 'Real Estate', 'Inventory'], p=[0.4, 0.3, 0.3])
        elif bt == 'Tech/Startup':
            ctype = np.random.choice(['None', 'Receivables'], p=[0.7, 0.3])
        else:
            ctype = np.random.choice(collateral_types, p=[0.3, 0.2, 0.2, 0.2, 0.1])
            
        collateral_type.append(ctype)
        
        # Value
        if ctype == 'None':
            collateral_value.append(0)
        else:
            coverage = np.random.uniform(0.5, 2.0)
            collateral_value.append(int(la * coverage))
            
    # --- Target: Default Flag (0/1) ---
    # Complex heuristic to simulate ground truth
    default_prob_list = []
    
    for i in range(num_records):
        score = 0 # Log-odds score essentially
        
        # 1. Credit History Impact (Strongest)
        if credit_scores[i] < 600: score += 2.5
        elif credit_scores[i] < 700: score += 1.0
        elif credit_scores[i] > 780: score -= 1.0
        
        if prior_default_history[i] == 1: score += 2.0
        
        # 2. Financial Health
        if dscr[i] < 1.0: score += 2.0
        elif dscr[i] < 1.25: score += 1.0
        elif dscr[i] > 2.0: score -= 1.0
        
        if net_margins[i] < 0: score += 1.5
        
        # 3. Business Stability
        if years_in_opp[i] < 2: score += 1.0
        
        # 4. Collateral
        c_coverage = collateral_value[i] / loan_amount[i]
        if c_coverage < 0.5: score += 0.5
        if coverage > 1.5: score -= 0.5
        
        # 5. Industry Risk (Tech/Construction slightly riskier)
        if business_types[i] in ['Tech/Startup', 'Construction']: score += 0.3
        
        # Sigmoid to probability
        # P(Default) = 1 / (1 + exp(-score + offset))
        # Adjust offset to get ~15-20% default rate overall
        prob = 1 / (1 + np.exp(-(score - 3.0))) 
        default_prob_list.append(prob)
        
    default_prob_list = np.array(default_prob_list)
    # Add some randomness (aleatoric uncertainty)
    default_flag = np.random.binomial(1, default_prob_list)

    # --- DataFrame ---
    df = pd.DataFrame({
        'applicant_id': ids,
        'business_type': business_types,
        'years_in_operation': years_in_opp,
        'promoter_credit_score': credit_scores,
        'promoter_exp_years': promoter_exp,
        'prior_default': prior_default_history,
        
        'annual_revenue': annual_revenue,
        'gst_turnover': gst_turnover,
        'ebitda_margin': np.round(ebitda_margins, 4),
        'net_margin': np.round(net_margins, 4),
        'total_debt': total_debt,
        'existing_emi': existing_emi,
        
        'loan_amount_requested': loan_amount,
        'loan_tenure_months': loan_tenure,
        'loan_purpose': loan_purpose,
        'proposed_emi': np.round(proposed_emi, 0).astype(int),
        'dscr': np.round(dscr, 2),
        
        'collateral_type': collateral_type,
        'collateral_value': collateral_value,
        
        'default_probability_true': np.round(default_prob_list, 4),
        'default_flag': default_flag
    })
    
    # Save
    output_dir = os.path.join('backend', 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'synthetic_credit_data.csv')
    df.to_csv(output_path, index=False)
    
    # Also save the schema for reference
    schema_info = {
        'num_records': num_records,
        'default_rate': float(df['default_flag'].mean()),
        'columns': list(df.columns)
    }
    with open(os.path.join(output_dir, 'schema_info.json'), 'w') as f:
        json.dump(schema_info, f, indent=4)
        
    print(f"Generated {num_records} records.")
    print(f"Default Rate: {df['default_flag'].mean():.2%}")
    print(f"Saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    generate_dataset()
